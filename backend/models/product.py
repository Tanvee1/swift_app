from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

@dataclass
class Product:
    id: int
    name: str
    category: str
    price: float
    stock: str
    stock_count: int
    rating: float
    location: str
    description: str
    image: str

    @property
    def is_in_stock(self) -> bool:
        return str(self.stock).strip().lower() in ['yes', 'true', '1'] and self.stock_count > 0

    @property
    def stock_status(self) -> str:
        return 'In Stock' if self.is_in_stock else 'Out of Stock'

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "price": self.price,
            "stock": self.stock,
            "stock_count": self.stock_count,
            "stock_status": self.stock_status,
            "rating": self.rating,
            "location": self.location,
            "description": self.description,
            "image": self.image
        }

@dataclass
class CartItem:
    product_id: int
    name: str
    price: float
    quantity: int
    category: str
    image: str

    @property
    def item_total(self) -> float:
        return round(self.price * self.quantity, 2)

@dataclass
class SearchFilter:
    query: Optional[str] = None
    category: Optional[str] = None
    max_price: Optional[float] = None
    min_price: Optional[float] = None
    aisle: Optional[str] = None
    in_stock_only: bool = False
    sort_by: str = "popularity"

@dataclass
class ChatMessage:
    role: str
    content: str
    products: List[Dict[str, Any]] = field(default_factory=list)
