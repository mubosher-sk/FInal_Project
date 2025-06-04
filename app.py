from flask import Flask, render_template
from flask_session import Session
from pymongo import MongoClient
from routes.auth_routes import auth_bp
import os

app = Flask(__name__)

# ===== Configurations =====
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "your_secret_key_here")

# Session config (to keep user logged in)
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# ===== Blueprints (will add routes later) =====
# from routes.auth_routes import auth_bp
# from routes.book_routes import book_bp
# app.register_blueprint(auth_bp)
# app.register_blueprint(book_bp)

# ===== Simple Home Route =====
@app.route("/")
def index():
    return render_template("index.html")

app.register_blueprint(auth_bp)
if __name__ == "__main__":
    app.run(debug=True)
