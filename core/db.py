"""
OPSHE SDK — Database Layer
"""

import sqlite3
from pathlib import Path

DB_PATH = Path("C:/opshe/opshe_db/opshe_test.db")

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def query(sql, params=()):
    conn = get_conn()
    try:
        rows = conn.execute(sql, params).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()

def execute(sql, params=()):
    conn = get_conn()
    try:
        cur = conn.execute(sql, params)
        conn.commit()
        return cur.rowcount
    finally:
        conn.close()

def find_similar_shades(lab_l, lab_a, lab_b, limit=10, max_delta_e=30):
    sql = (
        "SELECT s.shade_id, s.shade_name, s.shade_number, "
        "s.hex, s.rgb_r, s.rgb_g, s.rgb_b, "
        "s.lab_l, s.lab_a, s.lab_b, "
        "s.undertone, s.color_family, s.opacity, s.gloss_level, "
        "s.confidence, s.try_count, "
        "p.product_id, p.product_name, p.finish, p.price_idr, "
        "b.brand_id, b.brand_name, "
        "ROUND(SQRT("
        "(s.lab_l - ?)*(s.lab_l - ?) +"
        "(s.lab_a - ?)*(s.lab_a - ?) +"
        "(s.lab_b - ?)*(s.lab_b - ?)"
        "), 2) AS delta_e "
        "FROM shades s "
        "JOIN products p ON s.product_id = p.product_id "
        "JOIN brands b ON s.brand_id = b.brand_id "
        "ORDER BY delta_e ASC "
        "LIMIT ?"
    )
    rows = query(sql, (lab_l, lab_l, lab_a, lab_a, lab_b, lab_b, limit))
    return [r for r in rows if r["delta_e"] <= max_delta_e]