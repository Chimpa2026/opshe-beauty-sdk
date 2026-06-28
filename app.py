"""
OPSHE Beauty AR SDK — Main Application
"""

import sys
import os
import sqlite3

sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, jsonify, redirect
from pathlib import Path
from datetime import datetime

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False

from routes.api   import api
from routes.admin import admin

app.register_blueprint(api)
app.register_blueprint(admin)

@app.route("/")
def root():
    return redirect("/admin")

@app.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "service": "OPSHE Beauty AR SDK",
        "version": "1.0"
    })

from flask import send_from_directory

@app.route("/ar")
def ar_demo():
    return send_from_directory(
        os.path.dirname(__file__),
        "ar_demo.html"
    )

@app.errorhandler(404)
def not_found(e):
    return jsonify({"success": False, "error": "Endpoint tidak ditemukan"}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"success": False, "error": str(e)}), 500

def ensure_db():
    import os
    # Path otomatis — works di laptop maupun Railway
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DB_PATH  = Path(os.path.join(BASE_DIR, "opshe.db"))

    # Update DB_PATH di core/db.py
    import core.db as db_module
    db_module.DB_PATH = DB_PATH

    if not DB_PATH.exists():
        print("Database belum ada — membuat baru...")
        _create_db(DB_PATH)

    from core.makeover_inject import inject
    import core.makeover_inject as mi
    mi.DB_PATH = DB_PATH
    inject()
    return True

def _create_db(DB_PATH):
    import sqlite3, json
    from pathlib import Path

    SCHEMA = """
    CREATE TABLE IF NOT EXISTS brands (
        brand_id TEXT PRIMARY KEY, brand_name TEXT,
        country TEXT DEFAULT 'Indonesia', price_segment TEXT,
        halal_certified INTEGER DEFAULT 0, bpom_registered INTEGER DEFAULT 1
    );
    CREATE TABLE IF NOT EXISTS products (
        product_id TEXT PRIMARY KEY, brand_id TEXT, product_name TEXT,
        series TEXT, product_type TEXT, finish TEXT, price_idr INTEGER
    );
    CREATE TABLE IF NOT EXISTS shades (
        shade_id TEXT PRIMARY KEY, product_id TEXT, brand_id TEXT,
        shade_number TEXT, shade_name TEXT, hex TEXT,
        rgb_r INTEGER, rgb_g INTEGER, rgb_b INTEGER,
        lab_l REAL, lab_a REAL, lab_b REAL,
        undertone TEXT, color_family TEXT, depth TEXT,
        opacity INTEGER DEFAULT 95, gloss_level INTEGER DEFAULT 5,
        confidence INTEGER DEFAULT 75, verified INTEGER DEFAULT 0,
        try_count INTEGER DEFAULT 0
    );
    """

    # Cari master JSON — coba beberapa lokasi
    possible = [
        Path("C:/opshe/opshe_scraper/output/opshe_lips_master_v2.json"),
        Path(__file__).parent / "opshe_lips_master_v2.json",
        Path(__file__).parent.parent / "opshe_scraper/output/opshe_lips_master_v2.json",
    ]

    master_file = None
    for p in possible:
        if p.exists():
            master_file = p
            break

    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA)

    if master_file:
        print(f"Memuat data dari {master_file}...")
        master = json.loads(master_file.read_text(encoding='utf-8'))
        _insert_master(conn, master)
    else:
        print("Master JSON tidak ditemukan — DB kosong, hanya Make Over yang akan di-inject")

    conn.commit()
    conn.close()
    print(f"Database dibuat: {DB_PATH}")

def _insert_master(conn, master):
    GLOSS  = {'gloss':85,'glossy_tint':75,'satin':45,'soft_matte':20,'tint':30,'velvet_matte':8,'matte':5}
    OPACITY= {'matte':97,'velvet_matte':95,'soft_matte':88,'satin':85,'tint':60,'gloss':80}

    for brand in master.get("brands", []):
        bid = brand["brand_id"]
        conn.execute(
            "INSERT OR REPLACE INTO brands (brand_id,brand_name,country,price_segment,halal_certified,bpom_registered) VALUES (?,?,?,?,?,?)",
            (bid, brand["brand_name"], brand.get("brand_country","Indonesia"),
             "mid", 1 if brand.get("halal_certified") else 0, 1)
        )
        for product in brand.get("products", []):
            pid    = product["product_id"]
            finish = product.get("finish","matte")
            conn.execute(
                "INSERT OR REPLACE INTO products (product_id,brand_id,product_name,series,product_type,finish,price_idr) VALUES (?,?,?,?,?,?,?)",
                (pid, bid, product["product_name"], product.get("series",""),
                 product.get("product_type",""), finish, product.get("price_idr"))
            )
            gloss = GLOSS.get(finish,15)
            opac  = OPACITY.get(finish,90)
            for shade in product.get("shades", []):
                rgb = shade.get("rgb",{}); lab = shade.get("lab",{})
                conn.execute(
                    "INSERT OR REPLACE INTO shades (shade_id,product_id,brand_id,shade_number,shade_name,hex,rgb_r,rgb_g,rgb_b,lab_l,lab_a,lab_b,undertone,color_family,depth,opacity,gloss_level,confidence,verified) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (shade["shade_id"], pid, bid,
                     shade.get("shade_number",""), shade["shade_name"], shade["hex"],
                     rgb.get("r",0), rgb.get("g",0), rgb.get("b",0),
                     lab.get("L",50), lab.get("a",0), lab.get("b",0),
                     shade.get("undertone","neutral"), "neutral", "medium",
                     opac, gloss, shade.get("confidence",75),
                     1 if shade.get("verified") else 0)
                )

if __name__ == "__main__":
    print("=" * 55)
    print("OPSHE Beauty AR SDK")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 55)

    if not ensure_db():
        sys.exit(1)

    DB_PATH = "C:/opshe/opshe_db/opshe_test.db"
    conn    = sqlite3.connect(DB_PATH)
    brands   = conn.execute("SELECT COUNT(*) FROM brands").fetchone()[0]
    products = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
    shades   = conn.execute("SELECT COUNT(*) FROM shades").fetchone()[0]
    pending  = conn.execute(
        "SELECT COUNT(*) FROM shades WHERE confidence<75 AND verified=0"
    ).fetchone()[0]
    conn.close()

    print(f"\nDatabase:")
    print(f"  Brands   : {brands}")
    print(f"  Products : {products}")
    print(f"  Shades   : {shades}")
    print(f"  Pending  : {pending} shades butuh verifikasi")
    print(f"\nServer running di:")
    print(f"  http://localhost:5000        → Admin Panel")
    print(f"  http://localhost:5000/api/v1/brands  → API")
    print("=" * 55)
    print("\nTekan Ctrl+C untuk stop server")

    app.run(debug=True, port=5000, host="0.0.0.0")