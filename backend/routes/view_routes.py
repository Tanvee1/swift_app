from flask import Blueprint, render_template, request
from backend.services.search_service import SearchService

view_bp = Blueprint("views", __name__)
search_service = SearchService()

@view_bp.route("/")
def home():
    all_prods = [p.to_dict() for p in search_service.products]
    daily_utility = [p for p in all_prods if p.get('category') in ['Household', 'Dairy', 'Hygiene', 'Beverages']]
    sweets_snacks = [p for p in all_prods if p.get('category') in ['Snacks', 'Health', 'Cosmetics', 'Electronics', 'Fresh Produce']]
    return render_template("index.html", daily_utility=daily_utility, sweets_snacks=sweets_snacks)

@view_bp.route("/chat")
def chat():
    return render_template("chatbot.html")

@view_bp.route("/map")
def store_map():
    all_prods = [p.to_dict() for p in search_service.products]
    aisles = {}
    for p in all_prods:
        loc = p.get('location', 'General')
        aisles.setdefault(loc, []).append(p.get('name'))
    return render_template("map.html", aisles=aisles)

@view_bp.route("/trending")
def trending():
    all_prods = [p.to_dict() for p in search_service.products]
    return render_template("trending.html", products=all_prods)
