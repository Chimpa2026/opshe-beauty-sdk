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
    DB_PATH = Path("C:/opshe/opshe_db/opshe_test.db")
    if not DB_PATH.exists():
        print("ERROR: Database belum ada!")
        print("Jalankan dulu: python C:\\opshe\\opshe_db\\import_db.py")
        return False
    from core.makeover_inject import inject
    inject()
    return True

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