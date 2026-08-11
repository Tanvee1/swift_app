from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import pandas as pd
from openai import OpenAI
import os
import difflib
import re

app = Flask(__name__)
CORS(app)

# Load product data
PRODUCTS_CSV = os.path.join(os.path.dirname(__file__), "products.csv")

def get_product_list():
    df = pd.read_csv(PRODUCTS_CSV)
    df['stock_status'] = df['stock'].astype(str).str.strip().str.lower().apply(lambda x: 'In Stock' if x in ['yes', 'true', '1'] else 'Out of Stock')
    return df.to_dict(orient="records")

@app.route("/")
def home():
    all_products = get_product_list()
    daily_utility = [p for p in all_products if p.get('category') in ['Household', 'Dairy', 'Hygiene']]
    sweets_snacks = [p for p in all_products if p.get('category') in ['Snacks', 'Health', 'Cosmetics', 'Electronics']]
    return render_template("index.html", daily_utility=daily_utility, sweets_snacks=sweets_snacks)

@app.route("/chat")
def chat():
    return render_template("chatbot.html")

@app.route("/map")
def store_map():
    all_products = get_product_list()
    aisles = {}
    for p in all_products:
        loc = p.get('location', 'General')
        aisles.setdefault(loc, []).append(p.get('name'))
    return render_template("map.html", aisles=aisles)

@app.route("/trending")
def trending():
    all_products = get_product_list()
    return render_template("trending.html", products=all_products)

@app.route("/api/products", methods=["GET"])
def api_products():
    query = request.args.get("q", "").lower().strip()
    category = request.args.get("category", "").lower().strip()
    all_products = get_product_list()

    filtered = all_products
    if query:
        filtered = [
            p for p in filtered
            if query in p['name'].lower() or query in p['category'].lower() or query in p['description'].lower()
        ]
    if category:
        filtered = [p for p in filtered if p['category'].lower() == category]

    return jsonify({"products": filtered})

@app.route("/chat", methods=["POST"])
def chat_api():
    payload = request.get_json(silent=True) or {}
    user_msg = payload.get("message", "").lower().strip()

    if not user_msg:
        return jsonify({"reply": "Hello! How can I help you in SwiftShop today?", "products": []})

    all_products = get_product_list()
    matched_products = []

    # 1. Price extraction (e.g. "under 100", "below 500")
    price_match = re.search(r'(?:under|below|less than|within)\s*(?:₹|rs\.?|inr)?\s*(\d+)', user_msg)
    max_price = int(price_match.group(1)) if price_match else None

    # 2. Aisle extraction (e.g. "aisle 1", "aisle 3")
    aisle_match = re.search(r'aisle\s*(\d+)', user_msg)
    target_aisle = f"aisle {aisle_match.group(1)}" if aisle_match else None

    # 3. Token extraction (ignore common stop words & generic terms)
    stop_words = {
        'aisle', 'tell', 'show', 'items', 'item', 'product', 'products', 
        'with', 'from', 'have', 'does', 'what', 'which', 'where', 'some', 
        'give', 'list', 'about', 'need', 'want', 'find', 'locate'
    }
    tokens = [t for t in user_msg.split() if len(t) > 2 and t not in stop_words]

    for p in all_products:
        p_name = p['name'].lower()
        p_cat = p['category'].lower()
        p_desc = p['description'].lower()
        p_loc = p['location'].lower()

        # Enforce aisle constraint if specified
        if target_aisle and p_loc != target_aisle:
            continue

        # Enforce price constraint if specified
        if max_price is not None and p['price'] > max_price:
            continue

        # If user searched specific item/category terms
        if tokens:
            is_name_match = any(t in p_name for t in tokens)
            is_cat_match = any(t in p_cat for t in tokens)
            is_desc_match = any(t in p_desc for t in tokens)
            is_loc_match = any(t in p_loc for t in tokens)

            if is_name_match or is_cat_match or is_desc_match or is_loc_match:
                matched_products.append(p)
        elif target_aisle or max_price is not None:
            # Query specified aisle or price without specific item keywords
            matched_products.append(p)

    # Fallback fuzzy match if no direct token hit and no aisle/price constraint
    if not matched_products and not price_match and not target_aisle:
        product_names = [p['name'].lower() for p in all_products]
        close = difflib.get_close_matches(user_msg, product_names, n=2, cutoff=0.35)
        if close:
            matched_products = [p for p in all_products if p['name'].lower() in close]

    # Format reply text if catalog items matched
    if matched_products:
        lines = []
        if target_aisle:
            lines.append(f"I found **{len(matched_products)}** item(s) in **{target_aisle.title()}**:\n")
        else:
            lines.append(f"I found **{len(matched_products)}** item(s) matching your request:\n")
            
        for p in matched_products[:3]:
            lines.append(f"• **{p['name']}** ({p['category']}) - ₹{p['price']} | Status: **{p['stock_status']}** | Location: **{p['location']}**")
        
        reply_text = "\n".join(lines)
        return jsonify({
            "reply": reply_text,
            "products": matched_products[:4]
        })

    # Try OpenAI GPT if valid API key exists
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if openai_api_key and openai_api_key.startswith("sk-"):
        try:
            client = OpenAI(api_key=openai_api_key)
            catalog_summary = "\n".join([
                f"- {p['name']} ({p['category']}): ₹{p['price']}, Location: {p['location']}, Status: {p['stock_status']}, Description: {p['description']}"
                for p in all_products
            ])
            system_prompt = (
                "You are SwiftShop Assistant, a helpful retail shopping assistant for SwiftShop. "
                "Here is our complete store inventory:\n"
                f"{catalog_summary}\n"
                "Answer the customer clearly, concisely, and professionally without using unnecessary emojis."
            )
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_msg}
                ],
                max_tokens=250
            )
            reply = response.choices[0].message.content.strip()
            return jsonify({"reply": reply, "products": []})
        except Exception as e:
            print(f"OpenAI API Exception: {e}")

    # Professional Local Assistant Fallback (No Emojis)
    if any(w in user_msg for w in ["hi", "hello", "hey", "greetings"]):
        reply = "Hello! Welcome to SwiftShop. I can help you locate products, check aisle locations, view prices, or check stock availability."
    elif "map" in user_msg or "layout" in user_msg or ("where" in user_msg and "store" in user_msg):
        reply = "You can check our interactive store layout on the Store Map page. Aisles range from Aisle 1 (Snacks) to Aisle 7 (Dairy)."
    elif "hours" in user_msg or "open" in user_msg or "timing" in user_msg:
        reply = "SwiftShop is open daily from 8:00 AM to 10:00 PM."
    elif "discount" in user_msg or "offer" in user_msg or "sale" in user_msg:
        reply = "Check out our Trending page for featured popular items and daily budget picks."
    else:
        reply = (
            "I couldn't find an exact match in our inventory for that query. "
            "Try searching by category (such as Hygiene, Dairy, Snacks, Electronics), "
            "or ask something like 'Where is Dettol?' or 'Items under 100'."
        )

    return jsonify({"reply": reply, "products": []})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print(f"Launching SwiftShop on http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)
