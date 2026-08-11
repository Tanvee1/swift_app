import json
import os
from typing import List, Dict, Any, Tuple
from openai import OpenAI
from backend.services.search_service import SearchService
from backend.config import Config

class AIAgentService:
    def __init__(self, search_service: SearchService):
        self.search_service = search_service
        self.sessions: Dict[str, List[Dict[str, Any]]] = {}
        self.api_key = Config.OPENAI_API_KEY
        self.client = OpenAI(api_key=self.api_key) if self.api_key and self.api_key.startswith("sk-") else None

    def get_session_history(self, session_id: str) -> List[Dict[str, Any]]:
        if session_id not in self.sessions:
            self.sessions[session_id] = []
        return self.sessions[session_id]

    def add_message(self, session_id: str, role: str, content: str):
        history = self.get_session_history(session_id)
        history.append({"role": role, "content": content})
        # Keep last 10 turns for token efficiency
        if len(history) > 20:
            self.sessions[session_id] = history[-20:]

    def process_user_message(self, session_id: str, user_message: str) -> Tuple[str, List[Dict[str, Any]]]:
        self.add_message(session_id, "user", user_message)
        clean_msg = user_message.lower().strip()
        from datetime import datetime
        now = datetime.now()

        # 0. Check explicit conversational / general QA triggers first
        if "date" in clean_msg or "today" in clean_msg:
            reply = f"Today's date is **{now.strftime('%A, %B %d, %Y')}**."
            self.add_message(session_id, "assistant", reply)
            return reply, []
        elif "time" in clean_msg:
            reply = f"The current time is **{now.strftime('%I:%M %p')}**."
            self.add_message(session_id, "assistant", reply)
            return reply, []
        elif any(w in clean_msg for w in ["hi", "hello", "hey", "greetings"]):
            reply = "Hello! Welcome to SwiftShop. I can help you locate products, check aisle locations, view prices, or check stock availability."
            self.add_message(session_id, "assistant", reply)
            return reply, []
        elif "map" in clean_msg or "layout" in clean_msg or ("where" in clean_msg and "store" in clean_msg):
            reply = "You can check our interactive store layout on the Store Map page. Aisles range from Aisle 1 (Snacks) to Aisle 7 (Dairy)."
            self.add_message(session_id, "assistant", reply)
            return reply, []
        elif "hours" in clean_msg or "open" in clean_msg or "timing" in clean_msg:
            reply = "SwiftShop is open daily from 8:00 AM to 10:00 PM."
            self.add_message(session_id, "assistant", reply)
            return reply, []

        # 1. Run Hybrid Search Service to find catalog hits
        matched_products, s_filter = self.search_service.search(user_message, limit=4)
        matched_dicts = [p.to_dict() for p in matched_products]

        # Formulate formatted reply for product search hits
        if matched_products and (s_filter.aisle or s_filter.max_price is not None or len(matched_products) > 0):
            if s_filter.aisle:
                reply = f"I found **{len(matched_products)}** item(s) in **{s_filter.aisle.title()}**:\n"
            elif s_filter.max_price:
                reply = f"I found **{len(matched_products)}** budget item(s) under **₹{int(s_filter.max_price)}**:\n"
            else:
                reply = f"I found **{len(matched_products)}** item(s) matching your request:\n"

            for p in matched_products[:3]:
                reply += f"• **{p.name}** ({p.category}) - ₹{p.price} | Status: **{p.stock_status}** | Location: **{p.location}**\n"

            self.add_message(session_id, "assistant", reply)
            return reply, matched_dicts

        # 2. OpenAI Function Calling / Conversational Agent
        if self.client:
            try:
                catalog_summary = "\n".join([
                    f"- {p.name} ({p.category}): ₹{p.price}, Location: {p.location}, Stock: {p.stock_status}"
                    for p in self.search_service.products
                ])
                system_prompt = (
                    "You are SwiftShop Assistant, an enterprise retail AI assistant. "
                    "You assist users in navigating SwiftShop, checking stock, finding product locations, and building shopping lists. "
                    f"Current Inventory Overview:\n{catalog_summary}\n"
                    "Be helpful, professional, and clear."
                )
                
                messages = [{"role": "system", "content": system_prompt}] + self.get_session_history(session_id)
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=messages,
                    max_tokens=250
                )
                reply = response.choices[0].message.content.strip()
                self.add_message(session_id, "assistant", reply)
                return reply, []
            except Exception as e:
                print(f"OpenAI API Exception: {e}")

        # 3. Rule-based Smart Fallback Assistant
        clean_msg = user_message.lower().strip()
        from datetime import datetime
        now = datetime.now()

        if any(w in clean_msg for w in ["hi", "hello", "hey", "greetings"]):
            reply = "Hello! Welcome to SwiftShop. I can help you locate products, check aisle locations, view prices, or check stock availability."
        elif "date" in clean_msg or "today" in clean_msg or "day" in clean_msg:
            reply = f"Today's date is **{now.strftime('%A, %B %d, %Y')}**."
        elif "time" in clean_msg:
            reply = f"The current time is **{now.strftime('%I:%M %p')}**."
        elif "map" in clean_msg or "layout" in clean_msg or ("where" in clean_msg and "store" in clean_msg):
            reply = "You can check our interactive store layout on the Store Map page. Aisles range from Aisle 1 (Snacks) to Aisle 7 (Dairy)."
        elif "hours" in clean_msg or "open" in clean_msg or "timing" in clean_msg:
            reply = "SwiftShop is open daily from 8:00 AM to 10:00 PM."
        elif "discount" in clean_msg or "offer" in clean_msg or "sale" in clean_msg:
            reply = "Check out our Trending page for featured popular items and daily budget picks."
        else:
            reply = (
                "I couldn't find an exact match in our inventory for that query. "
                "Try searching by category (such as Hygiene, Dairy, Snacks, Electronics), "
                "or ask something like 'Where is Dettol?' or 'Items under 100'."
            )

        self.add_message(session_id, "assistant", reply)
        return reply, []
