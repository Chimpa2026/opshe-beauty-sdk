"""
OPSHE SDK — REST API Routes
"""

from flask import Blueprint, jsonify, request
from datetime import datetime
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from core.db import query, execute, find_similar_shades

api = Blueprint("api", __name__, url_prefix="/api/v1")

# ─── Helpers ─────────────────────────────────────────────────────────────────

def ok(data, meta=None):
    resp = {"success": True, "data": data}
    if meta:
        resp["meta"] = meta
    return jsonify(resp), 200

def err(msg, code=400):
    return jsonify({"success": False, "error": msg}), code

def paginate(rows, page, per_page):
    total = len(rows)
    start = (page - 1) * per_page
    end   = start + per_page
    return rows[start:end], {
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page
    }

# ─── BRANDS ──────────────────────────────────────────────────────────────────

@api.route("/brands", methods=["GET"])
def get_brands():
    rows = query("""
        SELECT
            b.brand_id, b.brand_name, b.country, b.price_segment,
            b.halal_certified, b.bpom_registered,
            COUNT(DISTINCT p.product_id) AS total_products,
            COUNT(DISTINCT s.shade_id)   AS total_shades,
            ROUND(AVG(s.confidence), 1)  AS avg_confidence
        FROM brands b
        LEFT JOIN products p ON b.brand_id   = p.brand_id
        LEFT JOIN shades   s ON p.product_id = s.product_id
        GROUP BY b.brand_id, b.brand_name, b.country,
                 b.price_segment, b.halal_certified, b.bpom_registered
        ORDER BY total_shades DESC
    """)
    return ok(rows, {"total": len(rows)})

@api.route("/brands/<brand_id>/products", methods=["GET"])
def get_brand_products(brand_id):
    rows = query("""
        SELECT p.*, COUNT(s.shade_id) AS shade_count
        FROM products p
        LEFT JOIN shades s ON p.product_id = s.product_id
        WHERE p.brand_id = ?
        GROUP BY p.product_id
        ORDER BY p.product_name
    """, (brand_id,))
    if not rows:
        return err(f"Brand '{brand_id}' tidak ditemukan", 404)
    return ok(rows, {"brand_id": brand_id, "total_products": len(rows)})

# ─── SHADES ──────────────────────────────────────────────────────────────────

@api.route("/shades", methods=["GET"])
def get_shades():
    brand_id   = request.args.get("brand_id")
    product_id = request.args.get("product_id")
    finish     = request.args.get("finish")
    undertone  = request.args.get("undertone")
    family     = request.args.get("family")
    min_conf   = int(request.args.get("min_confidence", 0))
    verified   = request.args.get("verified")
    page       = max(1, int(request.args.get("page", 1)))
    per_page   = min(200, max(1, int(request.args.get("per_page", 50))))

    where  = ["1=1"]
    params = []

    if brand_id:
        where.append("s.brand_id = ?"); params.append(brand_id)
    if product_id:
        where.append("s.product_id = ?"); params.append(product_id)
    if finish:
        where.append("p.finish = ?"); params.append(finish)
    if undertone:
        where.append("s.undertone = ?"); params.append(undertone)
    if family:
        where.append("s.color_family = ?"); params.append(family)
    if min_conf:
        where.append("s.confidence >= ?"); params.append(min_conf)
    if verified == "true":
        where.append("s.verified = 1")
    elif verified == "false":
        where.append("s.verified = 0")

    sql = f"""
        SELECT
            s.shade_id, s.shade_number, s.shade_name,
            s.hex, s.rgb_r, s.rgb_g, s.rgb_b,
            s.lab_l, s.lab_a, s.lab_b,
            s.undertone, s.color_family, s.depth,
            s.opacity, s.gloss_level,
            s.confidence, s.verified, s.try_count,
            p.product_id, p.product_name, p.series, p.finish, p.price_idr,
            b.brand_id, b.brand_name, b.halal_certified
        FROM shades s
        JOIN products p ON s.product_id = p.product_id
        JOIN brands   b ON s.brand_id   = b.brand_id
        WHERE {' AND '.join(where)}
        ORDER BY b.brand_name, p.product_name, s.shade_number
    """

    rows = query(sql, tuple(params))
    paged, meta = paginate(rows, page, per_page)
    meta["filters"] = {k: v for k, v in request.args.items()
                       if k not in ("page", "per_page")}
    return ok(paged, meta)

@api.route("/shades/<shade_id>", methods=["GET"])
def get_shade(shade_id):
    rows = query("""
        SELECT s.*, p.product_name, p.series, p.finish,
               p.product_type, p.price_idr,
               b.brand_name, b.country, b.halal_certified
        FROM shades s
        JOIN products p ON s.product_id = p.product_id
        JOIN brands   b ON s.brand_id   = b.brand_id
        WHERE s.shade_id = ?
    """, (shade_id,))
    if not rows:
        return err(f"Shade '{shade_id}' tidak ditemukan", 404)
    execute(
        "UPDATE shades SET try_count = try_count + 1 WHERE shade_id = ?",
        (shade_id,)
    )
    return ok(rows[0])

@api.route("/shades/similar", methods=["GET"])
def get_similar_shades():
    limit   = min(50, int(request.args.get("limit", 10)))
    max_de  = float(request.args.get("max_delta_e", 25))
    lab_l = lab_a = lab_b = None
    source_info = {}

    hex_input = request.args.get("hex", "").strip().lstrip("#")
    if hex_input:
        if len(hex_input) != 6:
            return err("Format HEX tidak valid. Contoh: #C02030")
        try:
            r = int(hex_input[0:2],16)
            g = int(hex_input[2:4],16)
            b = int(hex_input[4:6],16)
            def lin(c):
                c=c/255.0
                return c/12.92 if c<=0.04045 else ((c+0.055)/1.055)**2.4
            rl,gl,bl=lin(r),lin(g),lin(b)
            x=(rl*0.4124564+gl*0.3575761+bl*0.1804375)/0.95047
            y=(rl*0.2126729+gl*0.7151522+bl*0.0721750)/1.00000
            z=(rl*0.0193339+gl*0.1191920+bl*0.9503041)/1.08883
            def f(t): return t**(1/3) if t>0.008856 else 7.787*t+16/116
            fx,fy,fz=f(x),f(y),f(z)
            lab_l=round((116*fy)-16,2)
            lab_a=round(500*(fx-fy),2)
            lab_b=round(200*(fy-fz),2)
            source_info={"input_type":"hex","hex":f"#{hex_input.upper()}"}
        except:
            return err("HEX tidak valid")

    elif all(request.args.get(k) for k in ("lab_l","lab_a","lab_b")):
        lab_l=float(request.args.get("lab_l"))
        lab_a=float(request.args.get("lab_a"))
        lab_b=float(request.args.get("lab_b"))
        source_info={"input_type":"lab"}

    elif request.args.get("shade_id"):
        ref_id=request.args.get("shade_id")
        ref=query("SELECT lab_l,lab_a,lab_b,shade_name,hex FROM shades WHERE shade_id=?",(ref_id,))
        if not ref:
            return err(f"Shade referensi '{ref_id}' tidak ditemukan",404)
        lab_l,lab_a,lab_b=ref[0]["lab_l"],ref[0]["lab_a"],ref[0]["lab_b"]
        source_info={"input_type":"shade_id","reference":ref[0]}
    else:
        return err("Butuh salah satu parameter: hex, (lab_l+lab_a+lab_b), atau shade_id")

    results = find_similar_shades(lab_l, lab_a, lab_b, limit, max_de)
    return ok(results, {
        "source": source_info,
        "total_found": len(results),
        "max_delta_e": max_de,
        "note": "Delta-E < 5 = sangat mirip | < 10 = mirip | < 20 = agak mirip"
    })

# ─── ANALYTICS ───────────────────────────────────────────────────────────────

@api.route("/analytics/event", methods=["POST"])
def post_event():
    body       = request.get_json(silent=True) or {}
    event_type = body.get("event_type","").strip()
    shade_id   = body.get("shade_id","").strip()

    valid_events = {"view","try","save","share","buy_click"}
    if event_type not in valid_events:
        return err(f"event_type harus salah satu dari: {', '.join(valid_events)}")
    if not shade_id:
        return err("shade_id wajib diisi")

    shade = query("SELECT shade_id FROM shades WHERE shade_id=?",(shade_id,))
    if not shade:
        return err(f"Shade '{shade_id}' tidak ditemukan",404)

    execute(
        "UPDATE shades SET try_count = try_count + 1 WHERE shade_id=?",
        (shade_id,)
    )
    return jsonify({
        "success": True,
        "message": f"Event '{event_type}' recorded",
        "shade_id": shade_id,
        "timestamp": datetime.now().isoformat()
    }), 201

@api.route("/analytics/summary", methods=["GET"])
def get_analytics():
    top_shades = query("""
        SELECT s.shade_id, s.shade_name, s.hex, s.try_count,
               p.product_name, b.brand_name
        FROM shades s
        JOIN products p ON s.product_id = p.product_id
        JOIN brands   b ON s.brand_id   = b.brand_id
        ORDER BY s.try_count DESC LIMIT 10
    """)
    brand_summary = query("""
        SELECT b.brand_name,
               COUNT(DISTINCT p.product_id) AS products,
               COUNT(DISTINCT s.shade_id)   AS shades,
               SUM(s.try_count)             AS total_tries,
               ROUND(AVG(s.confidence),1)   AS avg_confidence
        FROM brands b
        LEFT JOIN products p ON b.brand_id   = p.brand_id
        LEFT JOIN shades   s ON p.product_id = s.product_id
        GROUP BY b.brand_id, b.brand_name
        ORDER BY total_tries DESC
    """)
    stats = query("""
        SELECT
            (SELECT COUNT(*) FROM brands)   AS total_brands,
            (SELECT COUNT(*) FROM products) AS total_products,
            (SELECT COUNT(*) FROM shades)   AS total_shades,
            (SELECT COUNT(*) FROM shades WHERE verified=1) AS verified_shades,
            (SELECT ROUND(AVG(confidence),1) FROM shades)  AS avg_confidence
    """)[0]
    return ok({
        "database": stats,
        "top_shades": top_shades,
        "brand_summary": brand_summary
    })

# ─── SEARCH ──────────────────────────────────────────────────────────────────

@api.route("/search", methods=["GET"])
def search_shades():
    q     = request.args.get("q","").strip()
    limit = min(100, int(request.args.get("limit",20)))
    if len(q) < 2:
        return err("Query minimal 2 karakter")
    pattern = f"%{q}%"
    rows = query("""
        SELECT s.shade_id, s.shade_name, s.shade_number,
               s.hex, s.undertone, s.color_family, s.confidence,
               p.product_name, p.finish, p.price_idr,
               b.brand_name, b.brand_id
        FROM shades s
        JOIN products p ON s.product_id = p.product_id
        JOIN brands   b ON s.brand_id   = b.brand_id
        WHERE LOWER(s.shade_name)   LIKE LOWER(?)
           OR LOWER(p.product_name) LIKE LOWER(?)
        ORDER BY s.confidence DESC
        LIMIT ?
    """, (pattern, pattern, limit))
    return ok(rows, {"query": q, "total_found": len(rows)})