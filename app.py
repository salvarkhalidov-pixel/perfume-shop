import os
import sqlite3
import json
from datetime import datetime
from functools import wraps

from flask import Flask, render_template, request, session, redirect, url_for

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key")

DB_NAME = "shop.db"

ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "1234")

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    db = get_db()
    db.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer TEXT NOT NULL,
            items TEXT NOT NULL,
            total INTEGER NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    db.commit()
    db.close()



init_db()



def money_kzt(n: int) -> str:
    return f"{n:,}".replace(",", " ") + " ₸"


def get_cart() -> dict:
    return session.get("cart", {})


def save_cart(cart: dict):
    session["cart"] = cart


def cart_count(cart: dict) -> int:
    return sum(cart.values())


def get_perfume_by_id(pid: str):
    for p in PERFUMES:
        if p["id"] == pid:
            return p
    return None


def build_cart_items(cart: dict):
    items = []
    total = 0
    for pid, qty in cart.items():
        p = get_perfume_by_id(pid)
        if not p:
            continue

        line_total = p["price"] * qty
        total += line_total

        items.append({
            "id": pid,
            "name": p["name"],
            "volume": p.get("volume", "14 мл"),
            "price": p["price"],
            "price_str": money_kzt(p["price"]),
            "qty": qty,
            "line_total": line_total,
            "line_total_str": money_kzt(line_total),
        })
    return items, total


def admin_required():
    if not session.get("is_admin"):
        return False
    return True
PERFUMES = [
    {"id": "molecule_02", "name": "Molecule 02 ", "price": 7500, "volume": "14мл"},
    # {"id": "bvlgari_tygar", "name": "Bvlgari Tygar ", "price": 9000, "volume": "14мл"},
    {"id": "antonio_banderas", "name": "Antonio Banderas ", "price": 7000, "volume": "14мл"},
    {"id": "oud_maracuja", "name": "Oud Maracuja ", "price": 9500, "volume": "14мл"},
    {"id": "armani_stronger_absolutely", "name": "Armani Stronger With You Absolutely ", "price": 8500, "volume": "14мл"},
    {"id": "armani_my_way", "name": "Armani My Way ", "price": 6500, "volume": "14мл"},
    {"id": "givenchy_ange_demon", "name": "Givenchy Ange ou Démon ", "price": 7000, "volume": "14мл"},

    {"id": "vs", "name": "Victoria's Secret Bombshell ", "price": 8700, "volume": "14мл"},
    {"id": "versace_bc", "name": "Versace Bright Crystal ", "price": 7790, "volume": "14мл"},
    {"id": "megamare", "name": "Orto Parisi Megamare ", "price": 10990, "volume": "14мл"},
    {"id": "sauvage", "name": "Dior Sauvage ", "price": 13990, "volume": "14мл"},

    {"id": "chanel_5", "name": "Chanel No.5 ", "price": 15990, "volume": "14мл"},
    {"id": "bleu_chanel", "name": "Bleu de Chanel ", "price": 14990, "volume": "14мл"},
    {"id": "black_opium", "name": "YSL Black Opium", "price": 13490, "volume": "14мл"},
    {"id": "lacoste_pour_femme", "name": "Lacoste Pour Femme ", "price": 9990, "volume": "14мл"},
    {"id": "armani_si", "name": "Giorgio Armani Si ", "price": 14490, "volume": "14мл"},
    {"id": "lanvin_eclat", "name": "Lanvin Éclat d'Arpège ", "price": 10490, "volume": "14мл"},
]



def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    db = get_db()
    db.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer TEXT NOT NULL,
            phone TEXT NOT NULL,
            address TEXT NOT NULL,
            items TEXT NOT NULL,
            total INTEGER NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    db.commit()
    db.close()



def money_kzt(n: int) -> str:
    return f"{n:,}".replace(",", " ") + " ₸"


def get_perfume_by_id(pid: str):
    for p in PERFUMES:
        if p["id"] == pid:
            return p
    return None


def get_cart() -> dict:
    return session.get("cart", {})


def save_cart(cart: dict):
    session["cart"] = cart


def cart_count(cart: dict) -> int:
    return sum(cart.values())


def build_cart_items(cart: dict):
    items = []
    total = 0

    for pid, qty in cart.items():
        p = get_perfume_by_id(pid)
        if not p:
            continue

        line_total = p["price"] * qty
        total += line_total

        items.append({
            "id": pid,
            "name": p["name"],
            "price": p["price"],
            "qty": qty,
            "price_str": money_kzt(p["price"]),
            "line_total": line_total,
            "line_total_str": money_kzt(line_total),
        })

    return items, total



def admin_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if not session.get("is_admin"):
            return redirect(url_for("admin_login"))
        return view_func(*args, **kwargs)
    return wrapper


@app.get("/admin")
def admin_login():
    return render_template("admin_login.html", error=None, cart_count=cart_count(get_cart()))


@app.post("/admin")
def admin_login_post():
    password = request.form.get("password", "")
    if password == ADMIN_PASSWORD:
        session["is_admin"] = True
        return redirect(url_for("orders_page"))
    return render_template("admin_login.html", error="Неверный пароль 😅", cart_count=cart_count(get_cart()))


@app.get("/admin/logout")
def admin_logout():
    session.pop("is_admin", None)
    return redirect(url_for("home"))


@app.get("/")
def home():
    cart = get_cart()
    return render_template(
        "index.html",
        perfumes=PERFUMES,
        money_kzt=money_kzt,
        cart_count=cart_count(cart),
    )


@app.get("/cart")
def cart_page():
    cart = get_cart()
    items, total = build_cart_items(cart)
    return render_template(
        "cart.html",
        items=items,
        total=total,
        total_str=money_kzt(total),
        cart_count=cart_count(cart),
    )


@app.post("/add-to-cart")
def add_to_cart():
    pid = request.form.get("perfume_id")
    cart = get_cart()
    if pid:
        cart[pid] = cart.get(pid, 0) + 1
        save_cart(cart)
    return redirect(url_for("home"))


@app.post("/cart/inc")
def cart_inc():
    pid = request.form.get("pid")
    cart = get_cart()
    if pid in cart:
        cart[pid] += 1
        save_cart(cart)
    return redirect(url_for("cart_page"))


@app.post("/cart/dec")
def cart_dec():
    pid = request.form.get("pid")
    cart = get_cart()
    if pid in cart:
        cart[pid] -= 1
        if cart[pid] <= 0:
            cart.pop(pid, None)
        save_cart(cart)
    return redirect(url_for("cart_page"))


@app.post("/cart/remove")
def cart_remove():
    pid = request.form.get("pid")
    cart = get_cart()
    cart.pop(pid, None)
    save_cart(cart)
    return redirect(url_for("cart_page"))


@app.post("/clear-cart")
def clear_cart():
    session.pop("cart", None)
    return redirect(url_for("cart_page"))


@app.get("/order")
def order_page():
    cart = get_cart()
    items, total = build_cart_items(cart)
    if not items:
        return redirect(url_for("cart_page"))

    return render_template(
        "order.html",
        items=items,
        total_str=money_kzt(total),
        cart_count=cart_count(cart),
    )


@app.post("/checkout")
def checkout():
    customer = (request.form.get("customer") or request.form.get("name") or "Без имени").strip()
    phone = (request.form.get("phone") or "").strip()
    address = (request.form.get("address") or "").strip()

    cart = get_cart()
    items, total = build_cart_items(cart)

    if not items:
        return redirect(url_for("cart_page"))

    if not phone or not address:
        return "Заполни все поля 😅", 400

    items_for_db = [
        {"name": it["name"], "price": it["price"], "qty": it["qty"], "line_total": it["line_total"]}
        for it in items
    ]

    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    db = get_db()
    cur = db.cursor()
    cur.execute(
        "INSERT INTO orders (customer, items, total, created_at) VALUES (?, ?, ?, ?)",
        (
            f"{customer} | {phone} | {address}",
            json.dumps(items_for_db, ensure_ascii=False),
            total,
            created_at
        )
    )
    db.commit()
    order_id = cur.lastrowid
    db.close()

    session.pop("cart", None)

    return render_template("success.html", order_id=order_id)


    session.pop("cart", None)

    return render_template("success.html", order_id=order_id)


@app.get("/orders")
@admin_required
def orders_page():
    db = get_db()
    rows = db.execute(
        "SELECT id, customer, phone, address, items, total, created_at FROM orders ORDER BY id DESC"
    ).fetchall()
    db.close()

    orders = []
    for r in rows:
        orders.append({
            "id": r["id"],
            "customer": r["customer"],
            "phone": r["phone"],
            "address": r["address"],
            "items": json.loads(r["items"]),
            "total_str": money_kzt(r["total"]),
            "created_at": r["created_at"],
        })

    return render_template(
        "orders.html",
        orders=orders,
        cart_count=cart_count(get_cart()),
    )


init_db()

if __name__ == "__main__":
    app.run(debug=True)
