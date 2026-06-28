"""
OPSHE SDK — Make Over Brand Injector (Brand ke-5)
"""
import sqlite3
from pathlib import Path

import os
BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__))).parent
DB_PATH  = BASE_DIR / "opshe.db"

def rgb_to_lab(rgb):
    r,g,b = [x/255.0 for x in rgb]
    def lin(c): return c/12.92 if c<=0.04045 else ((c+0.055)/1.055)**2.4
    r,g,b = lin(r),lin(g),lin(b)
    x=(r*0.4124564+g*0.3575761+b*0.1804375)/0.95047
    y=(r*0.2126729+g*0.7151522+b*0.0721750)/1.00000
    z=(r*0.0193339+g*0.1191920+b*0.9503041)/1.08883
    def f(t): return t**(1/3) if t>0.008856 else 7.787*t+16/116
    fx,fy,fz=f(x),f(y),f(z)
    return round((116*fy)-16,1),round(500*(fx-fy),1),round(200*(fy-fz),1)

def hex_to_rgb(h):
    h=h.lstrip('#')
    return int(h[0:2],16),int(h[2:4],16),int(h[4:6],16)

def detect_family(h):
    r,g,b=hex_to_rgb(h); br=(r+g+b)/3
    if r>180 and g<120 and b<120: return 'pink' if b>100 else 'red'
    if r>160 and g>100 and b<120: return 'coral_orange'
    if r>150 and g<100 and b>80: return 'berry'
    if r>120 and g<80 and b<80: return 'deep_red'
    if br>160: return 'nude_light'
    if r>140 and g>100 and b>80: return 'nude_medium'
    if r>100 and g>60 and b>50: return 'brown'
    return 'neutral'

def detect_depth(L):
    if L>=65: return 'light'
    if L>=50: return 'medium'
    if L>=35: return 'deep'
    return 'very_deep'

GLOSS  = {'gloss':85,'satin':45,'soft_matte':20,'tint':30,'velvet_matte':8,'matte':5}
OPAC   = {'matte':97,'velvet_matte':95,'soft_matte':88,'satin':85,'tint':60,'gloss':80}

PRODUCTS = [
    {"product_id":"MKO_LIP_001","product_name":"Powerstay Transferproof Matte Lip Cream",
     "series":"Powerstay","finish":"matte","product_type":"liquid_lipstick","price_idr":89000,
     "shades":[
        ("B01","No.1","#E08888","cool"),("B02","Amplify","#E090A0","cool"),
        ("B03","Curious","#E08070","warm"),("B04","Powerful","#D07888","cool"),
        ("B05","Popular","#C03040","warm"),("B06","M.O.","#A07060","warm"),
        ("B07","Hype","#C49880","warm"),("B08","New Rules","#8B1830","cool"),
        ("B09","Feisty","#7A3030","warm"),("B10","MO Nude","#C49A80","neutral"),
        ("B11","New Ruler","#901838","cool"),("B12","Mastershade","#B07060","warm")]},
    {"product_id":"MKO_LIP_002","product_name":"Intense Matte Lip Cream",
     "series":"Intense Matte","finish":"matte","product_type":"liquid_lipstick","price_idr":75000,
     "shades":[
        ("001","Lavish","#8B2848","cool"),("002","Heiress","#A03050","cool"),
        ("003","Secret","#C07880","neutral"),("004","Vanity","#D08888","neutral"),
        ("005","Impulse","#C03040","neutral"),("006","Mischief","#E08060","warm"),
        ("007","Luscious","#D09070","warm"),("008","Libertine","#B06878","neutral"),
        ("009","Posh","#901838","cool"),("010","Lux","#7A1828","cool"),
        ("012","Couture","#C07888","neutral"),("013","Dainty","#E09898","neutral"),
        ("015","Coquette","#D08080","neutral"),("016","Pixie","#E07080","neutral"),
        ("017","Savvy","#A04060","cool"),("020","Style","#901848","cool")]},
    {"product_id":"MKO_LIP_003","product_name":"Powerstay Glazed Lock Lip Pigment",
     "series":"Powerstay Glazed","finish":"gloss","product_type":"liquid_lipstick","price_idr":119000,
     "shades":[
        ("D01","Lover","#E08898","cool"),("D02","Aura","#D07888","cool"),
        ("D03","Blushed","#E09090","neutral"),("D04","IYKYK","#C06878","cool"),
        ("D05","Candied","#E08070","warm"),("D06","Allure","#C84060","cool"),
        ("D07","Ombre","#B85868","neutral"),("D09","Crush","#D05878","cool"),
        ("D14","Cherry","#B03040","cool"),("D18","Duchess","#C07888","cool"),
        ("D20","Glaze","#D08888","neutral"),("D21","Petal","#E09098","cool"),
        ("D24","Velvet","#A03060","cool")]},
]

def inject():
    conn = sqlite3.connect(DB_PATH)
    existing = conn.execute(
        "SELECT COUNT(*) FROM brands WHERE brand_id='MAKEOVER_001'"
    ).fetchone()[0]

    if existing:
        print("  Make Over sudah ada di DB, skip.")
        conn.close()
        return

    print("  Menambahkan Make Over ke database...")
    conn.execute(
        "INSERT OR REPLACE INTO brands (brand_id,brand_name,country,price_segment,halal_certified,bpom_registered) VALUES (?,?,?,?,?,?)",
        ("MAKEOVER_001","Make Over","Indonesia","mid",1,1)
    )

    total = 0
    for p in PRODUCTS:
        conn.execute(
            "INSERT OR REPLACE INTO products (product_id,brand_id,product_name,series,product_type,finish,price_idr) VALUES (?,?,?,?,?,?,?)",
            (p["product_id"],"MAKEOVER_001",p["product_name"],p["series"],
             p["product_type"],p["finish"],p["price_idr"])
        )
        for code,name,hex_c,undertone in p["shades"]:
            sid = f"MKO_{p['product_id'].split('_')[-1]}_{code}"
            r,g,b = hex_to_rgb(hex_c)
            ll,la,lb = rgb_to_lab((r,g,b))
            family = detect_family(hex_c)
            depth  = detect_depth(ll)
            gloss  = GLOSS.get(p["finish"],15)
            opac   = OPAC.get(p["finish"],90)
            conn.execute(
                "INSERT OR REPLACE INTO shades (shade_id,product_id,brand_id,shade_number,shade_name,hex,rgb_r,rgb_g,rgb_b,lab_l,lab_a,lab_b,undertone,color_family,depth,opacity,gloss_level,confidence,verified) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (sid,p["product_id"],"MAKEOVER_001",code,name,hex_c,
                 r,g,b,ll,la,lb,undertone,family,depth,opac,gloss,78,0)
            )
            total += 1

    conn.commit()
    conn.close()
    print(f"  Make Over berhasil ditambahkan: {len(PRODUCTS)} produk, {total} shades")

if __name__ == "__main__":
    inject()