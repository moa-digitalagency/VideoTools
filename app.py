import os
from flask import Flask, send_from_directory
from flask_cors import CORS

from config import TEMPLATES_DIR
from routes import videos_bp, jobs_bp, stats_bp, tiktok_bp, cleanup_bp


def create_app():
    static_dir = os.path.join(TEMPLATES_DIR)
    css_dir = os.path.join(TEMPLATES_DIR, "css")
    js_dir = os.path.join(TEMPLATES_DIR, "js")
    
    app = Flask(__name__, 
                static_folder=static_dir, 
                static_url_path='/static')
    
    CORS(app)
    
    app.register_blueprint(videos_bp)
    app.register_blueprint(jobs_bp)
    app.register_blueprint(stats_bp)
    app.register_blueprint(tiktok_bp)
    app.register_blueprint(cleanup_bp)
    
    @app.route("/")
    def serve_index():
        return send_from_directory(TEMPLATES_DIR, "index.html")
    
    @app.route("/static/css/<path:filename>")
    def serve_css(filename):
        return send_from_directory(css_dir, filename)
    
    @app.route("/static/js/<path:filename>")
    def serve_js(filename):
        return send_from_directory(js_dir, filename)
    
    return app


app = create_app()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting VideoSplit Flask server on port {port}...")
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)
