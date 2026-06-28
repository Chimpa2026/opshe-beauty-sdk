"""
OPSHE Beauty AR SDK — Main Application
"""

import sys
import os
import sqlite3
import json

sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, jsonify, redirect, send_from_directory
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

@app.route("/ar")
def ar_demo():
    return send_from_directory(os.path.dirname(__file__), "ar_demo.html")

@app.route("/health")
def health():
    return jsonify({"status": "ok", "service": "OPSHE Beauty AR SDK", "version": "1.0"})

@app.errorhandler(404)
def not_found(e):
    return jsonify({"success": False, "error": "Endpoint tidak ditemukan"}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"success": False, "error": str(e)}), 500

# ─── DB Path ─────────────────────────────────────────────────────────────────

BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
DB_PATH  = BASE_DIR / "opshe.db"

# ─── Schema ──────────────────────────────────────────────────────────────────

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

GLOSS_MAP  = {'gloss':85,'glossy_tint':75,'satin':45,'soft_matte':20,
              'tint':30,'velvet_matte':8,'matte':5,'liquid_matte':5}
OPACITY_MAP= {'matte':97,'velvet_matte':95,'soft_matte':88,
              'satin':85,'tint':60,'gloss':80}

# ─── DB Init ─────────────────────────────────────────────────────────────────

def init_db():
    """Buat schema + insert data dari JSON"""
    import core.db as db_module
    import core.makeover_inject as mi
    db_module.DB_PATH = DB_PATH
    mi.DB_PATH        = DB_PATH

    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA)

    # Cek apakah data sudah ada
    count = conn.execute("SELECT COUNT(*) FROM brands").fetchone()[0]
    if count > 0:
        print(f"  DB sudah ada — {count} brands, skip insert")
        conn.close()
        mi.inject()
        return

    # Cari master JSON
    possible = [
        BASE_DIR / "opshe_lips_master_v2.json",
        BASE_DIR.parent / "opshe_scraper/output/opshe_lips_master_v2.json",
        Path("C:/opshe/opshe_scraper/output/opshe_lips_master_v2.json"),
    ]

    master_file = None
    for p in possible:
        if p.exists():
            master_file = p
            print(f"  JSON ditemukan: {p}")
            break

    if not master_file:
        print("  ERROR: opshe_lips_master_v2.json tidak ditemukan!")
        conn.close()
        return

    # Insert data
    print("  Memasukkan data shade...")
    master = json.loads(master_file.read_text(encoding='utf-8'))

    for brand in master.get("brands", []):
        bid = brand["brand_id"]
        conn.execute(
            "INSERT OR REPLACE INTO brands VALUES (?,?,?,?,?,?)",
            (bid, brand["brand_name"],
             brand.get("brand_country", "Indonesia"),
             "mid",
             1 if brand.get("halal_certified") else 0, 1)
        )
        for product in brand.get("products", []):
            pid    = product["product_id"]
            finish = product.get("finish", "matte")
            conn.execute(
                "INSERT OR REPLACE INTO products VALUES (?,?,?,?,?,?,?)",
                (pid, bid, product["product_name"],
                 product.get("series", ""),
                 product.get("product_type", ""),
                 finish, product.get("price_idr"))
            )
            gloss = GLOSS_MAP.get(finish, 15)
            opac  = OPACITY_MAP.get(finish, 90)
            for shade in product.get("shades", []):
                rgb = shade.get("rgb", {})
                lab = shade.get("lab", {})
                conn.execute(
                    "INSERT OR REPLACE INTO shades VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (shade["shade_id"], pid, bid,
                     shade.get("shade_number", ""),
                     shade["shade_name"], shade["hex"],
                     rgb.get("r", 0), rgb.get("g", 0), rgb.get("b", 0),
                     lab.get("L", 50), lab.get("a", 0), lab.get("b", 0),
                     shade.get("undertone", "neutral"),
                     "neutral", "medium", opac, gloss,
                     shade.get("confidence", 75),
                     1 if shade.get("verified") else 0,
                     0)
                )

    conn.commit()
    total = conn.execute("SELECT COUNT(*) FROM shades").fetchone()[0]
    conn.close()
    print(f"  Berhasil insert {total} shades!")

    # Inject Make Over
    mi.inject()

# ─── Run ─────────────────────────────────────────────────────────────────────

# Init DB saat aplikasi start
print("=" * 50)
print("OPSHE Beauty AR SDK")
print(f"DB Path: {DB_PATH}")
print("=" * 50)

init_db()

if __name__ == "__main__":
    conn = sqlite3.connect(DB_PATH)
    brands   = conn.execute("SELECT COUNT(*) FROM brands").fetchone()[0]
    shades   = conn.execute("SELECT COUNT(*) FROM shades").fetchone()[0]
    conn.close()
    print(f"Brands: {brands} | Shades: {shades}")
    print("Server: http://localhost:5000")
    app.run(debug=True, port=5000, host="0.0.0.0")