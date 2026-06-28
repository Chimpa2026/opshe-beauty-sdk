"""
OPSHE SDK — Admin Panel
"""

from flask import Blueprint, render_template_string, request, redirect, jsonify
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from core.db import query, execute

admin = Blueprint("admin", __name__, url_prefix="/admin")

# ─── Admin API ────────────────────────────────────────────────────────────────

@admin.route("/api/shade/<shade_id>/update", methods=["POST"])
def update_shade(shade_id):
    body    = request.get_json(silent=True) or {}
    hex_val = body.get("hex","").strip().upper()
    if not hex_val.startswith("#") or len(hex_val) != 7:
        return jsonify({"success": False, "error": "Format HEX tidak valid"}), 400
    h = hex_val.lstrip("#")
    try:
        r,g,b = int(h[0:2],16),int(h[2:4],16),int(h[4:6],16)
    except:
        return jsonify({"success": False, "error": "HEX tidak valid"}), 400
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
    note   = body.get("note","")
    verify = body.get("verify", True)
    execute("""
        UPDATE shades SET
            hex=?, rgb_r=?, rgb_g=?, rgb_b=?,
            lab_l=?, lab_a=?, lab_b=?,
            confidence=95, verified=?, note=?
        WHERE shade_id=?
    """, (hex_val,r,g,b,lab_l,lab_a,lab_b,1 if verify else 0,note,shade_id))
    return jsonify({"success":True,"shade_id":shade_id,"hex":hex_val,"confidence":95})

@admin.route("/api/shade/<shade_id>/verify", methods=["POST"])
def verify_shade(shade_id):
    execute("UPDATE shades SET verified=1, confidence=90 WHERE shade_id=?", (shade_id,))
    return jsonify({"success": True, "shade_id": shade_id})

@admin.route("/api/shades/pending", methods=["GET"])
def get_pending():
    rows = query("""
        SELECT s.shade_id, s.shade_name, s.shade_number, s.hex,
               s.confidence, s.undertone, s.color_family,
               p.product_name, p.finish, b.brand_name
        FROM shades s
        JOIN products p ON s.product_id = p.product_id
        JOIN brands   b ON s.brand_id   = b.brand_id
        WHERE s.confidence < 75 AND s.verified = 0
        ORDER BY s.confidence ASC
    """)
    return jsonify({"success": True, "data": rows, "total": len(rows)})

# ─── HTML Template ────────────────────────────────────────────────────────────

BASE = """<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>OPSHE Admin — {{ title }}</title>
<style>
  :root {
    --bg:#0f0f14; --surface:#1a1a24; --surface2:#242432;
    --border:#2e2e42; --accent:#e8607a; --text:#e8e8f0;
    --muted:#7878a0; --success:#4caf82; --warn:#f0a050;
  }
  * { box-sizing:border-box; margin:0; padding:0; }
  body { font-family:system-ui,sans-serif; background:var(--bg); color:var(--text); }
  .nav { background:var(--surface); border-bottom:1px solid var(--border);
         padding:0 24px; display:flex; align-items:center; gap:24px; height:56px; }
  .nav-logo { font-weight:700; font-size:18px; color:var(--accent); }
  .nav a { color:var(--muted); text-decoration:none; font-size:14px; }
  .nav a:hover, .nav a.active { color:var(--text); }
  .container { max-width:1400px; margin:0 auto; padding:32px 24px; }
  .page-title { font-size:24px; font-weight:700; margin-bottom:8px; }
  .page-sub { color:var(--muted); font-size:14px; margin-bottom:28px; }
  .grid-4 { display:grid; grid-template-columns:repeat(4,1fr); gap:16px; margin-bottom:28px; }
  .grid-2 { display:grid; grid-template-columns:1fr 1fr; gap:20px; }
  .card { background:var(--surface); border:1px solid var(--border); border-radius:12px; padding:20px; }
  .card-label { font-size:12px; color:var(--muted); text-transform:uppercase; letter-spacing:.8px; margin-bottom:8px; }
  .card-value { font-size:32px; font-weight:700; }
  .card-sub { font-size:13px; color:var(--muted); margin-top:4px; }
  .badge { display:inline-block; padding:3px 10px; border-radius:100px; font-size:12px; font-weight:500; }
  .badge-warn  { background:rgba(240,160,80,.15); color:var(--warn); }
  .badge-ok    { background:rgba(76,175,130,.15); color:var(--success); }
  .badge-muted { background:rgba(120,120,160,.12); color:var(--muted); }
  table { width:100%; border-collapse:collapse; font-size:14px; }
  th { padding:10px 14px; text-align:left; color:var(--muted); font-size:12px;
       text-transform:uppercase; letter-spacing:.6px; border-bottom:1px solid var(--border); }
  td { padding:12px 14px; border-bottom:1px solid rgba(46,46,66,.5); }
  tr:hover td { background:var(--surface2); }
  .swatch { width:32px; height:32px; border-radius:6px; border:2px solid rgba(255,255,255,.1); display:inline-block; }
  .btn { padding:7px 16px; border-radius:8px; border:none; cursor:pointer; font-size:13px; font-weight:500; }
  .btn-primary  { background:var(--accent); color:white; }
  .btn-secondary{ background:var(--surface2); color:var(--text); border:1px solid var(--border); }
  .btn-success  { background:var(--success); color:white; }
  .btn-sm { padding:4px 12px; font-size:12px; }
  .filter-bar { display:flex; gap:12px; margin-bottom:20px; flex-wrap:wrap; }
  select, input[type=text], textarea {
    background:var(--surface2); border:1px solid var(--border);
    color:var(--text); border-radius:8px; padding:8px 12px; font-size:14px; }
  input[type=color] { width:44px; height:44px; border:none; padding:2px; border-radius:8px; cursor:pointer; }
  .flex { display:flex; align-items:center; gap:10px; }
  .field { margin-bottom:16px; }
  .field label { display:block; font-size:13px; color:var(--muted); margin-bottom:6px; }
  .color-preview { width:100%; height:80px; border-radius:10px; border:2px solid var(--border);
                   display:flex; align-items:center; justify-content:center;
                   font-size:13px; font-weight:600; margin-bottom:16px; transition:background .2s; }
  #editModal { display:none; position:fixed; inset:0; background:rgba(0,0,0,.7);
               z-index:1000; align-items:center; justify-content:center; }
  #editModal.open { display:flex; }
  .modal-box { background:var(--surface); border:1px solid var(--border);
               border-radius:16px; padding:28px; width:480px; max-width:95vw; }
  .modal-title { font-size:18px; font-weight:700; margin-bottom:20px; }
  .toast { position:fixed; bottom:24px; right:24px; padding:14px 20px; border-radius:10px;
           font-size:14px; font-weight:500; opacity:0; transition:opacity .3s; z-index:9999; }
  .toast.show { opacity:1; }
  .toast.success { background:var(--success); color:white; }
  .toast.error   { background:#e85050; color:white; }
  .conf-bar { height:6px; border-radius:3px; background:var(--border); overflow:hidden; width:80px; margin-top:4px; }
  .conf-fill { height:100%; border-radius:3px; }
  .api-links a { display:inline-block; margin:3px; padding:5px 12px; background:var(--surface2);
                 border:1px solid var(--border); border-radius:6px; color:var(--muted);
                 text-decoration:none; font-size:12px; }
  .api-links a:hover { color:var(--text); }
</style>
</head>
<body>
<nav class="nav">
  <span class="nav-logo">⬡ OPSHE Admin</span>
  <a href="/admin" class="{{ 'active' if active=='dashboard' else '' }}">Dashboard</a>
  <a href="/admin/shades" class="{{ 'active' if active=='shades' else '' }}">Shades</a>
  <a href="/admin/pending" class="{{ 'active' if active=='pending' else '' }}">
    Pending {% if pending_count %}<span class="badge badge-warn">{{ pending_count }}</span>{% endif %}
  </a>
  <span style="margin-left:auto; color:var(--muted); font-size:13px">OPSHE Beauty AR SDK v1.0</span>
</nav>
<div class="container">{{ content }}</div>

<div id="editModal">
  <div class="modal-box">
    <div class="modal-title">✏️ Edit Warna Shade</div>
    <div id="colorPreview" class="color-preview">Preview</div>
    <div class="field">
      <label>Shade</label>
      <div id="modalShadeName" style="font-weight:600;font-size:15px"></div>
      <div id="modalProduct" style="color:var(--muted);font-size:13px;margin-top:2px"></div>
    </div>
    <div class="field">
      <label>HEX Color</label>
      <div class="flex">
        <input type="color" id="colorPicker" oninput="syncColor(this.value,'picker')">
        <input type="text" id="hexInput" placeholder="#C02030" maxlength="7"
               oninput="syncColor(this.value,'text')" style="flex:1;font-family:monospace">
      </div>
    </div>
    <div class="field">
      <label>Note (opsional)</label>
      <textarea id="noteInput" rows="2" style="width:100%" placeholder="Contoh: Diverifikasi dari Shopee official store"></textarea>
    </div>
    <div style="display:flex;gap:10px;justify-content:flex-end;margin-top:20px">
      <button class="btn btn-secondary" onclick="closeModal()">Batal</button>
      <button class="btn btn-success btn-sm" onclick="saveShade(false)" style="padding:7px 16px">💾 Simpan</button>
      <button class="btn btn-primary" onclick="saveShade(true)">✅ Simpan & Verify</button>
    </div>
  </div>
</div>
<div id="toast" class="toast"></div>

<script>
let currentShadeId = null;
function openEdit(shadeId, shadeName, product, currentHex) {
  currentShadeId = shadeId;
  document.getElementById('modalShadeName').textContent = shadeName;
  document.getElementById('modalProduct').textContent = product;
  document.getElementById('hexInput').value = currentHex;
  document.getElementById('colorPicker').value = currentHex;
  document.getElementById('noteInput').value = '';
  updatePreview(currentHex);
  document.getElementById('editModal').classList.add('open');
}
function closeModal() {
  document.getElementById('editModal').classList.remove('open');
  currentShadeId = null;
}
function syncColor(val, from) {
  if (from === 'picker') {
    document.getElementById('hexInput').value = val.toUpperCase();
    updatePreview(val);
  } else {
    const clean = val.startsWith('#') ? val : '#'+val;
    if (/^#[0-9A-Fa-f]{6}$/.test(clean)) {
      document.getElementById('colorPicker').value = clean;
      updatePreview(clean);
    }
  }
}
function updatePreview(hex) {
  const el = document.getElementById('colorPreview');
  el.style.background = hex;
  const r=parseInt(hex.slice(1,3),16), g=parseInt(hex.slice(3,5),16), b=parseInt(hex.slice(5,7),16);
  el.style.color = (r*299+g*587+b*114)/1000 > 128 ? '#000' : '#fff';
  el.textContent = hex.toUpperCase();
}
async function saveShade(verify) {
  if (!currentShadeId) return;
  const hex  = document.getElementById('hexInput').value.trim();
  const note = document.getElementById('noteInput').value.trim();
  if (!/^#[0-9A-Fa-f]{6}$/.test(hex)) { showToast('Format HEX tidak valid','error'); return; }
  try {
    const res  = await fetch(`/admin/api/shade/${currentShadeId}/update`, {
      method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({hex, note, verify})
    });
    const data = await res.json();
    if (data.success) {
      showToast(verify ? '✅ Shade diverifikasi!' : '💾 Shade disimpan!', 'success');
      closeModal();
      setTimeout(() => location.reload(), 800);
    } else { showToast(data.error || 'Gagal menyimpan','error'); }
  } catch(e) { showToast('Network error','error'); }
}
async function quickVerify(shadeId) {
  const res = await fetch(`/admin/api/shade/${shadeId}/verify`,{method:'POST'});
  const data = await res.json();
  if (data.success) { showToast('✅ Verified!','success'); setTimeout(()=>location.reload(),600); }
}
function showToast(msg, type='success') {
  const el = document.getElementById('toast');
  el.textContent = msg; el.className = `toast ${type} show`;
  setTimeout(() => el.classList.remove('show'), 2800);
}
document.getElementById('editModal').addEventListener('click', function(e) {
  if (e.target === this) closeModal();
});
function applyFilter(key, val) {
  const url = new URL(window.location);
  if (val) url.searchParams.set(key, val); else url.searchParams.delete(key);
  window.location = url;
}
</script>
</body>
</html>"""

def render_admin(title, content, active="", pending_count=0):
    return render_template_string(
        BASE.replace("{{ content }}", content),
        title=title,
        active=active,
        pending_count=pending_count
    )

def get_pending_count():
    r = query("SELECT COUNT(*) as n FROM shades WHERE confidence < 75 AND verified = 0")
    return r[0]["n"] if r else 0

def conf_color(c):
    if c is None: return "#555"
    if c >= 85: return "#4caf82"
    if c >= 70: return "#f0a050"
    return "#e85050"

# ─── Dashboard ────────────────────────────────────────────────────────────────

@admin.route("/", methods=["GET"])
def dashboard():
    stats = query("""
        SELECT
            (SELECT COUNT(*) FROM brands)   AS brands,
            (SELECT COUNT(*) FROM products) AS products,
            (SELECT COUNT(*) FROM shades)   AS shades,
            (SELECT COUNT(*) FROM shades WHERE verified=1) AS verified,
            (SELECT COUNT(*) FROM shades WHERE confidence<75 AND verified=0) AS pending,
            (SELECT ROUND(AVG(confidence),1) FROM shades) AS avg_conf
    """)[0]

    brand_rows = query("""
        SELECT b.brand_name, b.country, b.price_segment,
               COUNT(DISTINCT p.product_id) AS products,
               COUNT(DISTINCT s.shade_id)   AS shades,
               COUNT(DISTINCT CASE WHEN s.verified=1 THEN s.shade_id END) AS verified,
               COUNT(DISTINCT CASE WHEN s.confidence<75 AND s.verified=0 THEN s.shade_id END) AS pending,
               ROUND(AVG(s.confidence),1) AS avg_conf
        FROM brands b
        LEFT JOIN products p ON b.brand_id   = p.brand_id
        LEFT JOIN shades   s ON p.product_id = s.product_id
        GROUP BY b.brand_id, b.brand_name, b.country, b.price_segment
        ORDER BY shades DESC
    """)

    cards = f"""
    <h1 class="page-title">Dashboard</h1>
    <p class="page-sub">OPSHE Lip Database — Status keseluruhan</p>
    <div class="grid-4">
      <div class="card">
        <div class="card-label">Total Brands</div>
        <div class="card-value">{stats['brands']}</div>
        <div class="card-sub">Wardah · Maybelline · Hanasui · BLP · Make Over</div>
      </div>
      <div class="card">
        <div class="card-label">Total Products</div>
        <div class="card-value">{stats['products']}</div>
        <div class="card-sub">Lip products aktif</div>
      </div>
      <div class="card">
        <div class="card-label">Total Shades</div>
        <div class="card-value">{stats['shades']}</div>
        <div class="card-sub">{stats['verified']} verified · {stats['pending']} pending</div>
      </div>
      <div class="card">
        <div class="card-label">Avg Confidence</div>
        <div class="card-value" style="color:{conf_color(stats['avg_conf'])}">{stats['avg_conf']}%</div>
        <div class="card-sub">Target: ≥ 85% semua shade</div>
      </div>
    </div>"""

    rows_html = ""
    for r in brand_rows:
        c = r['avg_conf'] or 0
        col = conf_color(c)
        flag = "🇮🇩" if r["country"] == "Indonesia" else "🇺🇸"
        pb = f'<span class="badge badge-warn">{r["pending"]} pending</span>' if r["pending"] else '<span class="badge badge-ok">✓ OK</span>'
        rows_html += f"""<tr>
          <td>{flag} <strong>{r['brand_name']}</strong></td>
          <td><span class="badge badge-muted">{r['price_segment'] or '-'}</span></td>
          <td>{r['products']}</td><td>{r['shades']}</td>
          <td style="color:{col};font-weight:600">{c}%
            <div class="conf-bar"><div class="conf-fill" style="width:{int(c)}%;background:{col}"></div></div>
          </td><td>{pb}</td>
          <td><a href="/admin/shades?brand={r['brand_name']}" class="btn btn-secondary btn-sm">Lihat →</a></td>
        </tr>"""

    content = cards + f"""
    <div class="grid-2">
      <div class="card">
        <div class="card-label" style="margin-bottom:16px">Brand Overview</div>
        <table>
          <tr><th>Brand</th><th>Segment</th><th>Produk</th><th>Shades</th><th>Confidence</th><th>Status</th><th></th></tr>
          {rows_html}
        </table>
      </div>
      <div class="card">
        <div class="card-label" style="margin-bottom:16px">Quick API Test</div>
        <div class="api-links">
          <a href="/api/v1/brands" target="_blank">GET /brands</a>
          <a href="/api/v1/shades?per_page=5" target="_blank">GET /shades</a>
          <a href="/api/v1/shades/similar?hex=%23C02030&limit=5" target="_blank">GET /similar</a>
          <a href="/api/v1/analytics/summary" target="_blank">GET /analytics</a>
          <a href="/api/v1/search?q=coral" target="_blank">GET /search?q=coral</a>
        </div>
        <div style="margin-top:20px">
          <a href="/admin/pending" class="btn btn-primary" style="display:inline-block">
            ⚠️ {stats['pending']} Shade Butuh Verifikasi →
          </a>
        </div>
      </div>
    </div>"""
    return render_admin("Dashboard", content, "dashboard", get_pending_count())

# ─── Shades List ──────────────────────────────────────────────────────────────

@admin.route("/shades", methods=["GET"])
def shades_list():
    brand_f    = request.args.get("brand","")
    conf_f     = request.args.get("conf","all")
    verified_f = request.args.get("verified","all")

    where = ["1=1"]; params = []
    if brand_f:
        where.append("b.brand_name LIKE ?"); params.append(f"%{brand_f}%")
    if conf_f == "low":
        where.append("s.confidence < 75")
    elif conf_f == "high":
        where.append("s.confidence >= 85")
    if verified_f == "yes":
        where.append("s.verified = 1")
    elif verified_f == "no":
        where.append("s.verified = 0")

    rows = query(f"""
        SELECT s.shade_id, s.shade_number, s.shade_name, s.hex,
               s.undertone, s.color_family, s.confidence, s.verified,
               p.product_name, p.finish, b.brand_name
        FROM shades s
        JOIN products p ON s.product_id = p.product_id
        JOIN brands   b ON s.brand_id   = b.brand_id
        WHERE {' AND '.join(where)}
        ORDER BY s.confidence ASC, b.brand_name
        LIMIT 300
    """, tuple(params))

    brands = query("SELECT brand_name FROM brands ORDER BY brand_name")
    bopts = "".join(f'<option value="{b["brand_name"]}" {"selected" if brand_f==b["brand_name"] else ""}>{b["brand_name"]}</option>' for b in brands)

    trows = ""
    for r in rows:
        c = r['confidence']; col = conf_color(c)
        vb = '<span class="badge badge-ok">✓ Verified</span>' if r['verified'] else '<span class="badge badge-warn">Pending</span>'
        sname = r['shade_name'].replace("'","\\'")
        pname = r['product_name'].replace("'","\\'")
        trows += f"""<tr>
          <td><div class="swatch" style="background:{r['hex']}"></div></td>
          <td style="font-family:monospace;font-size:13px">{r['hex']}</td>
          <td><strong>{r['shade_name']}</strong><div style="color:var(--muted);font-size:12px">{r['shade_number']}</div></td>
          <td>{r['brand_name']}</td>
          <td style="font-size:13px;color:var(--muted)">{r['product_name']}</td>
          <td><span class="badge badge-muted">{r['undertone']}</span></td>
          <td style="color:{col};font-weight:600">{c}%</td>
          <td>{vb}</td>
          <td>
            <button class="btn btn-secondary btn-sm" style="margin-right:4px"
              onclick="openEdit('{r['shade_id']}','{sname}','{pname}','{r['hex']}')">✏️ Edit</button>
            {"" if r['verified'] else f'<button class="btn btn-success btn-sm" onclick="quickVerify(\'{r["shade_id"]}\')">✓</button>'}
          </td>
        </tr>"""

    content = f"""
    <h1 class="page-title">Shade Manager</h1>
    <p class="page-sub">{len(rows)} shades ditampilkan</p>
    <div class="filter-bar">
      <select onchange="applyFilter('brand',this.value)">
        <option value="">Semua Brand</option>{bopts}
      </select>
      <select onchange="applyFilter('conf',this.value)">
        <option value="all" {"selected" if conf_f=="all" else ""}>Semua Confidence</option>
        <option value="low" {"selected" if conf_f=="low" else ""}>Low (&lt;75%)</option>
        <option value="high" {"selected" if conf_f=="high" else ""}>High (≥85%)</option>
      </select>
      <select onchange="applyFilter('verified',this.value)">
        <option value="all" {"selected" if verified_f=="all" else ""}>Semua Status</option>
        <option value="no"  {"selected" if verified_f=="no" else ""}>Belum Verified</option>
        <option value="yes" {"selected" if verified_f=="yes" else ""}>Sudah Verified</option>
      </select>
    </div>
    <div class="card" style="padding:0;overflow:hidden">
      <table>
        <tr><th>Color</th><th>HEX</th><th>Shade</th><th>Brand</th><th>Product</th><th>Undertone</th><th>Confidence</th><th>Status</th><th>Aksi</th></tr>
        {trows}
      </table>
    </div>"""
    return render_admin("Shade Manager", content, "shades", get_pending_count())

# ─── Pending ──────────────────────────────────────────────────────────────────

@admin.route("/pending", methods=["GET"])
def pending_list():
    rows = query("""
        SELECT s.shade_id, s.shade_number, s.shade_name, s.hex,
               s.confidence, s.undertone,
               p.product_name, b.brand_name
        FROM shades s
        JOIN products p ON s.product_id = p.product_id
        JOIN brands   b ON s.brand_id   = b.brand_id
        WHERE s.confidence < 75 AND s.verified = 0
        ORDER BY s.confidence ASC
    """)

    trows = ""
    for r in rows:
        sname = r['shade_name'].replace("'","\\'")
        pname = r['product_name'].replace("'","\\'")
        trows += f"""<tr>
          <td><div class="swatch" style="background:{r['hex']}"></div></td>
          <td style="font-family:monospace;font-size:13px">{r['hex']}</td>
          <td><strong>{r['shade_name']}</strong><div style="color:var(--muted);font-size:12px">{r['shade_number']}</div></td>
          <td>{r['brand_name']}</td>
          <td style="font-size:13px;color:var(--muted)">{r['product_name']}</td>
          <td style="color:#e85050;font-weight:600">{r['confidence']}%</td>
          <td>
            <button class="btn btn-primary btn-sm" style="margin-right:4px"
              onclick="openEdit('{r['shade_id']}','{sname}','{pname}','{r['hex']}')">✏️ Fix Color</button>
            <button class="btn btn-success btn-sm" onclick="quickVerify('{r['shade_id']}')">✓ Verify</button>
          </td>
        </tr>"""

    content = f"""
    <h1 class="page-title">⚠️ Pending Verification</h1>
    <p class="page-sub">{len(rows)} shade butuh koreksi warna manual</p>
    <div class="card" style="padding:0;overflow:hidden">
      <table>
        <tr><th>Color</th><th>HEX</th><th>Shade</th><th>Brand</th><th>Product</th><th>Confidence</th><th>Aksi</th></tr>
        {trows}
      </table>
    </div>
    <div style="margin-top:16px;padding:16px;background:var(--surface);border-radius:10px;font-size:13px;color:var(--muted)">
      💡 <strong>Tips:</strong> Buka Shopee official store brand, cari foto swatch produk,
      lalu klik ✏️ Fix Color dan masukkan HEX yang akurat. Target confidence ≥ 85%.
    </div>"""
    return render_admin("Pending Verification", content, "pending", len(rows))