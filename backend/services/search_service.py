import pandas as pd
import math
import difflib
import re
from collections import Counter
from typing import List, Dict, Any, Tuple
from backend.models.product import Product, SearchFilter
from backend.config import Config

class SearchService:
    def __init__(self, csv_path: str = Config.PRODUCTS_CSV):
        self.csv_path = csv_path
        self.products: List[Product] = []
        self.documents: List[List[str]] = []
        self.idf: Dict[str, float] = {}
        self.doc_vectors: List[Dict[str, float]] = []
        self.reload_catalog()

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r'\b\w+\b', text.lower())

    def reload_catalog(self):
        df = pd.read_csv(self.csv_path)
        self.products = []
        self.documents = []
        self.doc_vectors = []
        self.idf = {}

        N = len(df)
        df_counts = Counter()

        for _, row in df.iterrows():
            prod = Product(
                id=int(row['id']),
                name=str(row['name']),
                category=str(row['category']),
                price=float(row['price']),
                stock=str(row['stock']),
                stock_count=int(row.get('stock_count', 10 if str(row['stock']).lower() == 'yes' else 0)),
                rating=float(row.get('rating', 4.5)),
                location=str(row['location']),
                description=str(row['description']),
                image=str(row['image'])
            )
            self.products.append(prod)

            doc_text = f"{prod.name} {prod.category} {prod.description} {prod.location}"
            tokens = self._tokenize(doc_text)
            self.documents.append(tokens)
            for t in set(tokens):
                df_counts[t] += 1

        # Calculate inverse document frequency (IDF)
        for token, count in df_counts.items():
            self.idf[token] = math.log((N + 1.0) / (count + 1.0)) + 1.0

        # Build normalized TF-IDF document vectors
        for tokens in self.documents:
            tf = Counter(tokens)
            vec = {}
            norm = 0.0
            for token, count in tf.items():
                tfidf = (1.0 + math.log(count)) * self.idf[token]
                vec[token] = tfidf
                norm += tfidf ** 2
            norm = math.sqrt(norm) if norm > 0 else 1.0
            for token in vec:
                vec[token] /= norm
            self.doc_vectors.append(vec)

    def _cosine_similarity(self, query_tokens: List[str], doc_vec: Dict[str, float]) -> float:
        tf = Counter(query_tokens)
        q_vec = {}
        norm = 0.0
        for token, count in tf.items():
            if token in self.idf:
                tfidf = (1.0 + math.log(count)) * self.idf[token]
                q_vec[token] = tfidf
                norm += tfidf ** 2
        norm = math.sqrt(norm) if norm > 0 else 1.0

        sim = 0.0
        for token, q_val in q_vec.items():
            q_val_norm = q_val / norm
            if token in doc_vec:
                sim += q_val_norm * doc_vec[token]
        return sim

    def parse_query_intent(self, raw_query: str) -> Tuple[SearchFilter, List[str]]:
        raw_query_clean = raw_query.lower().strip()
        s_filter = SearchFilter()

        # 1. Price constraint
        price_match = re.search(r'(?:under|below|less than|within|max)\s*(?:₹|rs\.?|inr)?\s*(\d+)', raw_query_clean)
        if price_match:
            s_filter.max_price = float(price_match.group(1))

        # 2. Aisle constraint
        aisle_match = re.search(r'aisle\s*(\d+)', raw_query_clean)
        if aisle_match:
            s_filter.aisle = f"aisle {aisle_match.group(1)}"

        # 3. In-stock constraint
        if any(w in raw_query_clean for w in ['in stock', 'available', 'ready']):
            s_filter.in_stock_only = True

        stop_words = {
            'aisle', 'tell', 'show', 'items', 'item', 'product', 'products', 
            'with', 'from', 'have', 'does', 'what', 'which', 'where', 'some', 
            'give', 'list', 'about', 'need', 'want', 'find', 'locate', 'under',
            'below', 'less', 'than', 'price', 'cost', 'available', 'stock'
        }
        tokens = [t for t in self._tokenize(raw_query_clean) if len(t) > 2 and t not in stop_words and not t.isdigit()]
        return s_filter, tokens

    def search(self, raw_query: str, limit: int = 6) -> Tuple[List[Product], SearchFilter]:
        if not raw_query or not raw_query.strip():
            return self.products[:limit], SearchFilter()

        s_filter, tokens = self.parse_query_intent(raw_query)
        q_tokens = self._tokenize(raw_query)
        scored_results: List[Tuple[float, Product]] = []

        for idx, prod in enumerate(self.products):
            if s_filter.max_price is not None and prod.price > s_filter.max_price:
                continue
            if s_filter.aisle and prod.location.lower() != s_filter.aisle:
                continue
            if s_filter.in_stock_only and not prod.is_in_stock:
                continue
            if s_filter.category and prod.category.lower() != s_filter.category.lower():
                continue

            v_score = self._cosine_similarity(q_tokens, self.doc_vectors[idx]) * 3.0
            t_score = 0.0

            p_name_lower = prod.name.lower()
            p_cat_lower = prod.category.lower()
            p_desc_lower = prod.description.lower()

            for token in tokens:
                if token in p_name_lower:
                    t_score += 2.5
                elif token in p_cat_lower:
                    t_score += 1.5
                elif token in p_desc_lower:
                    t_score += 0.8

            match_score = v_score + t_score
            if match_score > 0.4 or (s_filter.aisle or s_filter.max_price is not None):
                total_score = match_score + (prod.rating * 0.1)
                scored_results.append((total_score, prod))

        if not scored_results and (s_filter.aisle or s_filter.max_price is not None):
            pass
        elif not scored_results and tokens:
            product_names = [p.name.lower() for p in self.products]
            close = difflib.get_close_matches(raw_query.lower(), product_names, n=3, cutoff=0.4)
            for p in self.products:
                if p.name.lower() in close:
                    scored_results.append((1.0, p))

        scored_results.sort(key=lambda x: x[0], reverse=True)
        final_products = [prod for score, prod in scored_results]

        return final_products[:limit], s_filter
