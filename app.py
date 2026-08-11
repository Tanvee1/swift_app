import os
from flask import Flask, jsonify
from flask_cors import CORS
from backend.config import Config
from backend.routes.api_routes import api_bp
from backend.routes.view_routes import view_bp

def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object(Config)
    CORS(app)

    # Register Blueprints
    app.register_blueprint(view_bp)
    app.register_blueprint(api_bp)

    # Global Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return jsonify({"error": "Resource not found", "status": 404}), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return jsonify({"error": "Internal server error", "status": 500}), 500

    return app

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", Config.DEFAULT_PORT))
    print(f"🚀 Launching Production SwiftShop Server on http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=Config.DEBUG)
