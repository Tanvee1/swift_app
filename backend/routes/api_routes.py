from flask import Blueprint, request, jsonify
from backend.services.search_service import SearchService
from backend.services.ai_agent_service import AIAgentService
import uuid

api_bp = Blueprint("api", __name__, url_prefix="/api")

search_service = SearchService()
ai_agent_service = AIAgentService(search_service)

@api_bp.route("/products", methods=["GET"])
def get_products():
    query = request.args.get("q", "")
    category = request.args.get("category", "")
    max_price_str = request.args.get("max_price", "")
    
    if query or category or max_price_str:
        products, _ = search_service.search(query, limit=50)
        if category:
            products = [p for p in products if p.category.lower() == category.lower()]
        if max_price_str and max_price_str.isdigit():
            products = [p for p in products if p.price <= float(max_price_str)]
        results = [p.to_dict() for p in products]
    else:
        results = [p.to_dict() for p in search_service.products]

    return jsonify({"count": len(results), "products": results})

@api_bp.route("/products/<int:product_id>", methods=["GET"])
def get_product_detail(product_id: int):
    for p in search_service.products:
        if p.id == product_id:
            return jsonify(p.to_dict())
    return jsonify({"error": "Product not found"}), 404

@api_bp.route("/chat", methods=["POST"])
def chat():
    payload = request.get_json(silent=True) or {}
    message = payload.get("message", "").strip()
    session_id = payload.get("session_id") or str(uuid.uuid4())

    if not message:
        return jsonify({
            "session_id": session_id,
            "reply": "Hello! How can I assist you at SwiftShop today?",
            "products": []
        })

    reply, products = ai_agent_service.process_user_message(session_id, message)
    return jsonify({
        "session_id": session_id,
        "reply": reply,
        "products": products
    })

@api_bp.route("/cart/calculate", methods=["POST"])
def calculate_cart():
    payload = request.get_json(silent=True) or {}
    items = payload.get("items", [])
    
    subtotal = 0.0
    item_breakdown = []
    
    for item in items:
        price = float(item.get("price", 0))
        qty = int(item.get("quantity", 1))
        tot = round(price * qty, 2)
        subtotal += tot
        item_breakdown.append({
            "name": item.get("name"),
            "price": price,
            "quantity": qty,
            "total": tot
        })
        
    tax = round(subtotal * 0.05, 2)  # 5% GST/Tax
    delivery_fee = 0.0 if subtotal > 500 or subtotal == 0 else 40.0
    grand_total = round(subtotal + tax + delivery_fee, 2)

    return jsonify({
        "items": item_breakdown,
        "subtotal": round(subtotal, 2),
        "tax": tax,
        "delivery_fee": delivery_fee,
        "grand_total": grand_total
    })
