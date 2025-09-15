
import os
import logging
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create Flask application
app = Flask(__name__)

# Set session secret
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")

# Configure proxy fix middleware
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Register blueprints
from routes import api_bp, web_bp

app.register_blueprint(api_bp)
app.register_blueprint(web_bp)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
