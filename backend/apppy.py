from flask import Flask
from flask_cors import CORS
from flask_caching import Cache
from routes import register_routes
from error_handlers import register_error_handlers

app = Flask(__name__)
CORS(app)

# Configure caching
cache = Cache(app, config={"CACHE_TYPE": "SimpleCache", "CACHE_DEFAULT_TIMEOUT": 300})

# Register routes and error handlers
register_routes(app, cache)
register_error_handlers(app)

if __name__ == "__main__":
    app.run(debug=True)
