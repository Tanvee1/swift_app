from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import pandas as pd
from openai import OpenAI
import os
import difflib

app = Flask(__name__)
CORS(app)

# Load product data
products = pd.read_csv("products.csv")

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat")
def chat():
    return render_template("chatbot.html")

@app.route("/map")
def store_map():
    return render_template("map.html")

@app.route("/trending")
def trending():
    top_products = products.head(12).to_dict(orient="records")  # More products
    return render_template("trending.html", products=top_products)

# Util function: best fuzzy match
def best_match(query, options):
    matches = difflib.get_close_matches(query, options, n=1, cutoff=0.4)
    return matches[0] if matches else None

@app.route("/chat", methods=["POST"])
def chat_api():
    user_msg = request.json.get("message", "").lower().strip()

    matched = products[
    products.apply(
        lambda row: any(
            term in row[col].lower()
            for col in ['name', 'category', 'description']
            for term in user_msg.split()
        ),
        axis=1
    )
]


    # Fallback: fuzzy match on keywords
    if matched.empty:
        product_names = products["name"].str.lower().tolist()
        best = difflib.get_close_matches(user_msg, product_names, n=1, cutoff=0.4)
        if best:
            matched = products[products["name"].str.lower() == best[0]]

    if not matched.empty:
        row = matched.iloc[0]
        aisle = row.get("location", "Unknown aisle")
        stock = " In Stock" if str(row["stock"]).strip().lower() == "yes" else " Out of Stock"
        reply = (
            f" *{row['name']}* ({row['category']})\n"
            f" ₹{row['price']} — {stock}\n"
            f" Location: {aisle}\n"
            f" {row['description']}"
        )
    else:
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
            {"role": "system", "content": "You are a helpful retail assistant for a smart store. You help users locate products, tell them aisle numbers, give availability info, and make product suggestions using friendly and clear language."},
            {"role": "user", "content": user_msg}
            ]
        )

            reply = response.choices[0].message.content.strip()
        except Exception as e:
            reply = f" GPT Error: {e}"

    return jsonify({"reply": reply})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
