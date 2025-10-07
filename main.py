from flask import Flask, render_template, redirect, url_for, session, request, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# ---------------- FLASK APP SETUP ---------------- #
app = Flask(__name__)
app.secret_key = "supersecretkey"

# Database config
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
db = SQLAlchemy(app)

# ---------------- USER MODEL ---------------- #
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)

# Create tables
with app.app_context():
    db.create_all()

# ---------------- DUMMY PRODUCTS ---------------- #
products_list = [
    {
        "id": 1,
        "name": "Laptop",
        "price": 1200,
        "image": "images/laptop.jpeg",
        "images": "images/laptop.jpeg",
        "description": "A high-performance laptop suitable for work, gaming, and entertainment."
    },
    {
        "id": 2,
        "name": "Phone",
        "price": 800,
        "image": "images/phones.jpeg",
        "images": "images/phones.jpeg",
        "description": "Latest smartphone with powerful camera and long-lasting battery."
    },
    {
        "id": 3,
        "name": "Headphones",
        "price": 150,
        "image": "images/headphones.jpeg",
        "images": "images/headphones.jpeg",
        "description": "Noise-cancelling headphones with immersive sound quality."
    },
    {
        "id": 4,
        "name": "Mouse",
        "price": 200,
        "image": "images/mouse.jpeg",
        "images": "images/mouse.jpeg",
        "description": "Ergonomic wireless mouse with fast response and comfort grip."
    }
]

# ---------------- ROUTES ---------------- #

@app.route("/")
def home():
    return render_template("home.html", title="Home")

@app.route("/about")
def about():
    return render_template("about.html", title="About")

# Products Page
@app.route("/products")
def show_products():
    return render_template("products.html", products=products_list)

# Add to Cart
@app.route("/add_to_cart/<int:product_id>")
def add_to_cart(product_id):
    if "cart" not in session:
        session["cart"] = []

    for product in products_list:
        if product["id"] == product_id:
            session["cart"].append(product)
            session.modified = True
            flash(f"{product['name']} added to cart!", "success")
            break

    return redirect(url_for("show_products"))

# Cart Page
@app.route("/cart")
def cart():
    cart_items = session.get("cart", [])
    total = sum(item["price"] for item in cart_items)
    return render_template("cart.html", cart=cart_items, total=total, title="Cart")

# Clear Cart
@app.route("/clear_cart")
def clear_cart():
    session["cart"] = []
    return redirect(url_for("cart"))

# Product Detail Page
@app.route("/product/<int:product_id>")
def product_detail(product_id):
    product = next((p for p in products_list if p["id"] == product_id), None)
    if product is None:
        return "Product not found", 404
    return render_template("product_detail.html", product=product)

# Signup
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()

        if existing_user:
            flash("Username or Email already exists!", "danger")
            return redirect(url_for("signup"))

        hashed_password = generate_password_hash(password, method="pbkdf2:sha256")
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash("Account created successfully! Please login.", "success")
        return redirect(url_for("login"))

    return render_template("signup.html", title="Sign Up")

# Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id
            session["username"] = user.username
            flash(f"Welcome back, {user.username}!", "success")
            return redirect(url_for("home"))
        else:
            flash("Invalid email or password!", "danger")

    return render_template("login.html", title="Login")

# Logout
@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("home"))

# ---------------- MAIN ---------------- #
if __name__ == "__main__":
    app.run(debug=True)
