"""
OPSHE Beauty AR SDK — Main Application
Data di-embed langsung — tidak perlu file JSON eksternal
"""

import sys, os, sqlite3, json
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
def index():
    return redirect("/ar")

@app.route("/ar")
def ar():
    return send_from_directory(os.path.dirname(__file__), "index.html")

@app.route("/lips")
def lips_realtime():
    # Alias untuk ar_demo.html (realtime mode dari landing page)
    return send_from_directory(os.path.dirname(__file__), "ar_demo.html")

@app.route("/admin-panel")
def admin_panel():
    return redirect("/admin")

@app.route("/logo")
def serve_logo():
    return send_from_directory(os.path.dirname(__file__), "logoopshe.png")

@app.route("/health")
def health():
    return jsonify({"status":"ok","service":"OPSHE Beauty AR SDK","version":"1.0"})

@app.errorhandler(404)
def not_found(e):
    return jsonify({"success":False,"error":"Endpoint tidak ditemukan"}),404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"success":False,"error":str(e)}),500

# ─── DB Config ───────────────────────────────────────────────────────────────

BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
DB_PATH  = BASE_DIR / "opshe.db"

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

BRANDS = [
    ("WARDAH_001",    "Wardah",            "Indonesia",     "mid", 1, 1),
    ("MAYBELLINE_001","Maybelline New York","USA",           "mid", 0, 1),
    ("HANASUI_001",   "Hanasui",           "Indonesia",     "mid", 1, 1),
    ("MAKEOVER_001",  "Make Over",         "Indonesia",     "mid", 1, 1),
    ("TIMEPHORIA_001","Timephoria",         "Indonesia",     "mid", 1, 1),
    ("PIXY_001",      "Pixy",              "Indonesia",     "mid", 1, 1),
    ("OMG_001",       "OMG",               "Indonesia",     "low", 1, 1),
    ("LATULIPE_001",  "Latulipe",          "Indonesia",     "mid", 1, 1),
    ("LTPRO_001",     "LTPRO",             "Indonesia",     "mid", 1, 1),
    ("BARENBLISS_001","Barenbliss",        "Korea Selatan", "mid", 0, 1),
    ("SOMETHINC_001", "Somethinc",         "Indonesia",     "mid", 1, 1),
]

PRODUCTS = [
    # Wardah
    ("WD_LIP_001","WARDAH_001","Wardah Long Lasting Lipstick","Long Lasting","lipstick_bullet","satin",None),
    ("WD_LIP_002","WARDAH_001","Wardah Exclusive Moist Lipstick","Exclusive","lipstick_bullet","satin",None),
    ("WD_LIP_003","WARDAH_001","Wardah Exclusive Matte Lipstick","Exclusive","lipstick_bullet","matte",None),
    ("WD_LIP_004","WARDAH_001","Wardah Colorfit Velvet Matte Lip Mousse","Colorfit","liquid_lipstick","velvet_matte",None),
    ("WD_LIP_005","WARDAH_001","Wardah Glasting Liquid Lip","Glasting","liquid_lip_gloss","gloss",None),
    ("WD_LIP_006","WARDAH_001","Wardah Everyday Cheek & Liptint","Everyday","lip_tint","tint",None),
    ("WD_LIP_007","WARDAH_001","Wardah Colorfit Ultralight Matte Lipstick","Colorfit","lipstick_bullet","matte",None),
    ("WD_LIP_008","WARDAH_001","Wardah Colorfit Last All Day Lip Paint","Colorfit","liquid_lipstick","matte",None),
    # Maybelline
    ("MBL_LIP_001","MAYBELLINE_001","SuperStay Matte Ink","SuperStay","liquid_lipstick","matte",132500),
    ("MBL_LIP_002","MAYBELLINE_001","SuperStay Vinyl Ink","SuperStay","liquid_lipstick","gloss",122500),
    ("MBL_LIP_003","MAYBELLINE_001","SuperStay Teddy Tint","SuperStay","lip_tint","soft_matte",112500),
    # Hanasui
    ("HNS_LIP_001","HANASUI_001","Mattedorable Lip Cream","Mattedorable","liquid_lipstick","velvet_matte",30500),
    ("HNS_LIP_002","HANASUI_001","Mattedorable Lip Cream Boba Edition","Mattedorable Boba","liquid_lipstick","velvet_matte",30500),
    ("HNS_LIP_003","HANASUI_001","Mattedorable Lip Cream Matcha Latte Edition","Mattedorable Matcha","liquid_lipstick","velvet_matte",32025),
    ("HNS_LIP_004","HANASUI_001","Mattedorable Lipstick","Mattedorable","lipstick_bullet","matte",35000),
    # Make Over
    ("MKO_LIP_001","MAKEOVER_001","Powerstay Transferproof Matte Lip Cream","Powerstay","liquid_lipstick","matte",89000),
    ("MKO_LIP_002","MAKEOVER_001","Intense Matte Lip Cream","Intense Matte","liquid_lipstick","matte",75000),
    ("MKO_LIP_003","MAKEOVER_001","Powerstay Glazed Lock Lip Pigment","Powerstay Glazed","liquid_lipstick","gloss",119000),
    # Timephoria
    ("TMP_LIP_001","TIMEPHORIA_001","Timephoria Nebula Velvet Lip Cream","Nebula","liquid_lipstick","velvet_matte",89000),
    ("TMP_LIP_002","TIMEPHORIA_001","Timephoria Stellar Dust Lip Stain","Stellar","lip_tint","tint",79000),
    ("TMP_LIP_003","TIMEPHORIA_001","Timephoria Eternal Lip Matte","Eternal","liquid_lipstick","matte",75000),
    # Pixy
    ("PIX_LIP_001","PIXY_001","Pixy Lip Cream","Lip Cream","liquid_lipstick","matte",46000),
    ("PIX_LIP_002","PIXY_001","Pixy Matte in Love","Matte in Love","lipstick_bullet","matte",40000),
    ("PIX_LIP_003","PIXY_001","Pixy Mousse Moments","Mousse Moments","liquid_lipstick","velvet_matte",55000),
    # OMG
    ("OMG_LIP_001","OMG_001","OMG Lip Cream","Lip Cream","liquid_lipstick","matte",25000),
    # Latulipe
    ("LTP_LIP_001","LATULIPE_001","Latulipe Matte Lip Cream","Matte","liquid_lipstick","matte",35000),
    ("LTP_LIP_002","LATULIPE_001","Latulipe True Color Lipstick","True Color","lipstick_bullet","satin",45000),
    # LTPRO
    ("LTPR_LIP_001","LTPRO_001","LTPRO Lip Glow Oil","Lip Glow","lip_gloss","gloss",55000),
    ("LTPR_LIP_002","LTPRO_001","LTPRO Matte Lip Cream","Matte","liquid_lipstick","matte",49000),
    # Barenbliss
    ("BNB_LIP_001","BARENBLISS_001","Barenbliss Cherry Makes Cheerful Lip Velvet","Cherry","liquid_lipstick","velvet_matte",89000),
    ("BNB_LIP_002","BARENBLISS_001","Barenbliss Peach Makes Perfect Liptint","Peach","lip_tint","tint",79000),
    ("BNB_LIP_003","BARENBLISS_001","Barenbliss Apple Makes Adorable Mousse Tint","Apple","lip_tint","soft_matte",85000),
    ("BNB_LIP_004","BARENBLISS_001","Barenbliss Vinyl Lip Cream","Vinyl","liquid_lipstick","gloss",79000),
    # Somethinc
    ("SMT_LIP_001","SOMETHINC_001","Somethinc IDOL Blurry Soft Lip Matte","IDOL","liquid_lipstick","soft_matte",79000),
    ("SMT_LIP_002","SOMETHINC_001","Somethinc Transferproof Lipstick","Transferproof","lipstick_bullet","matte",89000),
]

SHADES = [
    # WARDAH Long Lasting
    ("WD_LIP_001_01","WD_LIP_001","WARDAH_001","01","Fabulous Peach","#E89070","warm"),
    ("WD_LIP_001_02","WD_LIP_001","WARDAH_001","02","Pink Sorbet","#E08090","cool"),
    ("WD_LIP_001_03","WD_LIP_001","WARDAH_001","03","Simply Brown","#A06050","warm"),
    ("WD_LIP_001_04","WD_LIP_001","WARDAH_001","04","Antique Pink","#C07880","cool"),
    ("WD_LIP_001_05","WD_LIP_001","WARDAH_001","05","Fuschia Fever","#D03070","cool"),
    ("WD_LIP_001_06","WD_LIP_001","WARDAH_001","06","Delicate Pink","#E09098","cool"),
    ("WD_LIP_001_07","WD_LIP_001","WARDAH_001","07","Rapsberry Hip","#A02848","cool"),
    ("WD_LIP_001_08","WD_LIP_001","WARDAH_001","08","Red Velvet","#901830","cool"),
    ("WD_LIP_001_09","WD_LIP_001","WARDAH_001","09","Vibrant Red","#C02030","warm"),
    ("WD_LIP_001_10","WD_LIP_001","WARDAH_001","10","Stylish Mocca","#8B5040","warm"),
    ("WD_LIP_001_11","WD_LIP_001","WARDAH_001","11","Cherrie Glam","#A83050","cool"),
    ("WD_LIP_001_12","WD_LIP_001","WARDAH_001","12","Lustrous Red","#B02030","warm"),
    ("WD_LIP_001_13","WD_LIP_001","WARDAH_001","13","Classic Brown","#905040","warm"),
    ("WD_LIP_001_14","WD_LIP_001","WARDAH_001","14","Violet Pink","#C060A0","cool"),
    ("WD_LIP_001_15","WD_LIP_001","WARDAH_001","15","Rouge Red","#C01828","cool"),
    ("WD_LIP_001_16","WD_LIP_001","WARDAH_001","16","Smooth Latte","#B07868","warm"),
    ("WD_LIP_001_17","WD_LIP_001","WARDAH_001","17","Passionate Red","#B01830","cool"),
    ("WD_LIP_001_18","WD_LIP_001","WARDAH_001","18","Sunset Orange","#D06040","warm"),
    ("WD_LIP_001_19","WD_LIP_001","WARDAH_001","19","Sunrise Nude","#C49080","warm"),
    # WARDAH Colorfit Velvet
    ("WD_LIP_004_01","WD_LIP_004","WARDAH_001","01","Brown Dreamer","#A06848","warm"),
    ("WD_LIP_004_02","WD_LIP_004","WARDAH_001","02","Joyful Orange","#D06840","warm"),
    ("WD_LIP_004_03","WD_LIP_004","WARDAH_001","03","Rose Ballerina","#D07880","cool"),
    ("WD_LIP_004_04","WD_LIP_004","WARDAH_001","04","Pink Sweetheart","#E08090","cool"),
    ("WD_LIP_004_05","WD_LIP_004","WARDAH_001","05","Artisan Mauve","#B07888","cool"),
    ("WD_LIP_004_06","WD_LIP_004","WARDAH_001","06","Fuchsia Lover","#C03070","cool"),
    ("WD_LIP_004_07","WD_LIP_004","WARDAH_001","07","Red Pioneer","#B02030","warm"),
    ("WD_LIP_004_08","WD_LIP_004","WARDAH_001","08","Brown Creator","#A25A52","warm"),
    ("WD_LIP_004_09","WD_LIP_004","WARDAH_001","09","Ombre Charmer","#C08070","neutral"),
    ("WD_LIP_004_10","WD_LIP_004","WARDAH_001","10","Lively Coral","#E07060","warm"),
    ("WD_LIP_004_11","WD_LIP_004","WARDAH_001","11","Cherish Marmalade","#C08070","warm"),
    ("WD_LIP_004_12","WD_LIP_004","WARDAH_001","12","Chic Terracota","#B55540","warm"),
    ("WD_LIP_004_13","WD_LIP_004","WARDAH_001","13","Sweet Cinnamon","#955030","warm"),
    ("WD_LIP_004_14","WD_LIP_004","WARDAH_001","14","Dainty Caramel","#A06040","warm"),
    # WARDAH Glasting
    ("WD_LIP_005_01","WD_LIP_005","WARDAH_001","01","Caramel Coat","#C08868","warm"),
    ("WD_LIP_005_02","WD_LIP_005","WARDAH_001","02","Peach Polish","#E08870","warm"),
    ("WD_LIP_005_03","WD_LIP_005","WARDAH_001","03","Dazzle Maple","#C06848","warm"),
    ("WD_LIP_005_04","WD_LIP_005","WARDAH_001","04","Rosewood Radiance","#C07878","neutral"),
    ("WD_LIP_005_05","WD_LIP_005","WARDAH_001","05","Glazing Berry","#A02848","cool"),
    ("WD_LIP_005_06","WD_LIP_005","WARDAH_001","06","Ruby Sparks","#B02030","cool"),
    ("WD_LIP_005_14","WD_LIP_005","WARDAH_001","14","Latte Lacque","#A07858","warm"),
    ("WD_LIP_005_15","WD_LIP_005","WARDAH_001","15","Blossom Veil","#C08070","neutral"),
    # MAYBELLINE SuperStay Matte Ink
    ("MBL_001_015","MBL_LIP_001","MAYBELLINE_001","15","Lover","#D05060","cool"),
    ("MBL_001_020","MBL_LIP_001","MAYBELLINE_001","20","Pioneer","#C03040","cool"),
    ("MBL_001_025","MBL_LIP_001","MAYBELLINE_001","25","Heroine","#8B2040","cool"),
    ("MBL_001_050","MBL_LIP_001","MAYBELLINE_001","50","Voyager","#7A1828","cool"),
    ("MBL_001_060","MBL_LIP_001","MAYBELLINE_001","60","Poet","#C84858","cool"),
    ("MBL_001_065","MBL_LIP_001","MAYBELLINE_001","65","Seductress","#A83050","cool"),
    ("MBL_001_070","MBL_LIP_001","MAYBELLINE_001","70","Amazonian","#C02030","warm"),
    ("MBL_001_075","MBL_LIP_001","MAYBELLINE_001","75","Fighter","#B02830","neutral"),
    ("MBL_001_080","MBL_LIP_001","MAYBELLINE_001","80","Ruler","#901828","cool"),
    ("MBL_001_115","MBL_LIP_001","MAYBELLINE_001","115","Founder","#C05848","warm"),
    ("MBL_001_117","MBL_LIP_001","MAYBELLINE_001","117","Groundbreaker","#B04838","warm"),
    ("MBL_001_118","MBL_LIP_001","MAYBELLINE_001","118","Dancer","#D06858","warm"),
    ("MBL_001_120","MBL_LIP_001","MAYBELLINE_001","120","Artist","#E07060","warm"),
    ("MBL_001_125","MBL_LIP_001","MAYBELLINE_001","125","Inspirer","#D08070","warm"),
    ("MBL_001_130","MBL_LIP_001","MAYBELLINE_001","130","Selfstarter","#E09070","warm"),
    ("MBL_001_135","MBL_LIP_001","MAYBELLINE_001","135","Globetrotter","#C06850","warm"),
    ("MBL_001_150","MBL_LIP_001","MAYBELLINE_001","150","Savant","#A85040","warm"),
    ("MBL_001_155","MBL_LIP_001","MAYBELLINE_001","155","Pathfinder","#C07868","warm"),
    ("MBL_001_170","MBL_LIP_001","MAYBELLINE_001","170","Initiator","#E08878","warm"),
    ("MBL_001_205","MBL_LIP_001","MAYBELLINE_001","205","Assertive","#C85068","cool"),
    ("MBL_001_220","MBL_LIP_001","MAYBELLINE_001","220","Ambitious","#E08888","cool"),
    ("MBL_001_285","MBL_LIP_001","MAYBELLINE_001","285","Gritty","#6A1828","cool"),
    ("MBL_001_305","MBL_LIP_001","MAYBELLINE_001","305","Unconventional","#8B3058","cool"),
    ("MBL_001_500","MBL_LIP_001","MAYBELLINE_001","500","Insider","#A06858","warm"),
    ("MBL_001_510","MBL_LIP_001","MAYBELLINE_001","510","Charmer","#C08878","warm"),
    ("MBL_001_520","MBL_LIP_001","MAYBELLINE_001","520","Champion","#B07060","warm"),
    # MAYBELLINE Vinyl Ink
    ("MBL_002_010","MBL_LIP_002","MAYBELLINE_001","10","Lippy","#B04040","warm"),
    ("MBL_002_015","MBL_LIP_002","MAYBELLINE_001","15","Peachy","#E08870","warm"),
    ("MBL_002_020","MBL_LIP_002","MAYBELLINE_001","20","Coy","#D07880","neutral"),
    ("MBL_002_025","MBL_LIP_002","MAYBELLINE_001","25","Red Hot","#C02828","warm"),
    ("MBL_002_030","MBL_LIP_002","MAYBELLINE_001","30","Unrivaled","#8B2848","cool"),
    ("MBL_002_050","MBL_LIP_002","MAYBELLINE_001","50","Wicked","#901830","cool"),
    ("MBL_002_060","MBL_LIP_002","MAYBELLINE_001","60","Mischievous","#C84060","cool"),
    ("MBL_002_095","MBL_LIP_002","MAYBELLINE_001","95","Captivated","#C03050","cool"),
    ("MBL_002_115","MBL_LIP_002","MAYBELLINE_001","115","Peppy","#E07888","cool"),
    # MAYBELLINE Teddy Tint
    ("MBL_003_010","MBL_LIP_003","MAYBELLINE_001","10","Skinnydip","#E08888","cool"),
    ("MBL_003_015","MBL_LIP_003","MAYBELLINE_001","15","Punch","#D04870","cool"),
    ("MBL_003_020","MBL_LIP_003","MAYBELLINE_001","20","Apricot","#E08870","warm"),
    ("MBL_003_025","MBL_LIP_003","MAYBELLINE_001","25","Berry","#A02848","cool"),
    ("MBL_003_030","MBL_LIP_003","MAYBELLINE_001","30","Caramel","#A06040","warm"),
    ("MBL_003_035","MBL_LIP_003","MAYBELLINE_001","35","Nude","#C49070","neutral"),
    ("MBL_003_040","MBL_LIP_003","MAYBELLINE_001","40","Red","#C02030","neutral"),
    ("MBL_003_045","MBL_LIP_003","MAYBELLINE_001","45","Coral","#E07058","warm"),
    ("MBL_003_050","MBL_LIP_003","MAYBELLINE_001","50","Rose","#D06878","cool"),
    ("MBL_003_060","MBL_LIP_003","MAYBELLINE_001","60","Plum","#7A2060","cool"),
    ("MBL_003_070","MBL_LIP_003","MAYBELLINE_001","70","Cherry","#901830","cool"),
    ("MBL_003_095","MBL_LIP_003","MAYBELLINE_001","95","Wine","#7A1530","cool"),
    ("MBL_003_105","MBL_LIP_003","MAYBELLINE_001","105","Terracotta","#B85840","warm"),
    ("MBL_003_125","MBL_LIP_003","MAYBELLINE_001","125","Brick","#A04030","warm"),
    ("MBL_003_130","MBL_LIP_003","MAYBELLINE_001","130","Burgundy","#7A1828","cool"),
    # HANASUI Mattedorable
    ("HNS_001_01","HNS_LIP_001","HANASUI_001","01","Kiss","#C13248","cool"),
    ("HNS_001_02","HNS_LIP_001","HANASUI_001","02","Ruby","#A02030","cool"),
    ("HNS_001_03","HNS_LIP_001","HANASUI_001","03","Bold","#8B1A28","cool"),
    ("HNS_001_04","HNS_LIP_001","HANASUI_001","04","Chic","#D03058","cool"),
    ("HNS_001_05","HNS_LIP_001","HANASUI_001","05","Classy","#C09080","neutral"),
    ("HNS_001_06","HNS_LIP_001","HANASUI_001","06","Ritz","#D08870","warm"),
    ("HNS_001_07","HNS_LIP_001","HANASUI_001","07","Spark","#E09088","neutral"),
    ("HNS_001_08","HNS_LIP_001","HANASUI_001","08","Fancy","#C08870","warm"),
    ("HNS_001_09","HNS_LIP_001","HANASUI_001","09","Glow","#D07068","warm"),
    ("HNS_001_10","HNS_LIP_001","HANASUI_001","10","Bloom","#E08080","cool"),
    ("HNS_001_11","HNS_LIP_001","HANASUI_001","11","Brick","#B55040","warm"),
    ("HNS_001_12","HNS_LIP_001","HANASUI_001","12","Amaze","#D09880","warm"),
    ("HNS_001_13","HNS_LIP_001","HANASUI_001","13","Grace","#C07070","neutral"),
    ("HNS_001_14","HNS_LIP_001","HANASUI_001","14","Luxe","#901838","cool"),
    ("HNS_001_15","HNS_LIP_001","HANASUI_001","15","Posh","#A04050","cool"),
    ("HNS_001_16","HNS_LIP_001","HANASUI_001","16","Glam","#B07888","cool"),
    # HANASUI Boba Edition
    ("HNS_002_01","HNS_LIP_002","HANASUI_001","01","Forest Berry","#7A2040","cool"),
    ("HNS_002_02","HNS_LIP_002","HANASUI_001","02","Brown Sugar","#A06848","warm"),
    ("HNS_002_03","HNS_LIP_002","HANASUI_001","03","Salted Caramel","#B07050","warm"),
    ("HNS_002_04","HNS_LIP_002","HANASUI_001","04","Taro Milk","#C08898","cool"),
    ("HNS_002_05","HNS_LIP_002","HANASUI_001","05","Matcha Kiss","#8B5858","neutral"),
    ("HNS_002_06","HNS_LIP_002","HANASUI_001","06","Hazelnut Latte","#B07858","warm"),
    # MAKE OVER Powerstay
    ("MKO_001_B01","MKO_LIP_001","MAKEOVER_001","B01","No.1","#E08888","cool"),
    ("MKO_001_B02","MKO_LIP_001","MAKEOVER_001","B02","Amplify","#E090A0","cool"),
    ("MKO_001_B03","MKO_LIP_001","MAKEOVER_001","B03","Curious","#E08070","warm"),
    ("MKO_001_B04","MKO_LIP_001","MAKEOVER_001","B04","Powerful","#D07888","cool"),
    ("MKO_001_B05","MKO_LIP_001","MAKEOVER_001","B05","Popular","#C03040","warm"),
    ("MKO_001_B06","MKO_LIP_001","MAKEOVER_001","B06","M.O.","#A07060","warm"),
    ("MKO_001_B07","MKO_LIP_001","MAKEOVER_001","B07","Hype","#C49880","warm"),
    ("MKO_001_B08","MKO_LIP_001","MAKEOVER_001","B08","New Rules","#8B1830","cool"),
    ("MKO_001_B09","MKO_LIP_001","MAKEOVER_001","B09","Feisty","#7A3030","warm"),
    ("MKO_001_B10","MKO_LIP_001","MAKEOVER_001","B10","MO Nude","#C49A80","neutral"),
    ("MKO_001_B11","MKO_LIP_001","MAKEOVER_001","B11","New Ruler","#901838","cool"),
    ("MKO_001_B12","MKO_LIP_001","MAKEOVER_001","B12","Mastershade","#B07060","warm"),
    # MAKE OVER Intense Matte
    ("MKO_002_001","MKO_LIP_002","MAKEOVER_001","001","Lavish","#8B2848","cool"),
    ("MKO_002_002","MKO_LIP_002","MAKEOVER_001","002","Heiress","#A03050","cool"),
    ("MKO_002_003","MKO_LIP_002","MAKEOVER_001","003","Secret","#C07880","neutral"),
    ("MKO_002_005","MKO_LIP_002","MAKEOVER_001","005","Impulse","#C03040","neutral"),
    ("MKO_002_006","MKO_LIP_002","MAKEOVER_001","006","Mischief","#E08060","warm"),
    ("MKO_002_009","MKO_LIP_002","MAKEOVER_001","009","Posh","#901838","cool"),
    ("MKO_002_010","MKO_LIP_002","MAKEOVER_001","010","Lux","#7A1828","cool"),
    ("MKO_002_017","MKO_LIP_002","MAKEOVER_001","017","Savvy","#A04060","cool"),
    # MAKE OVER Glazed
    ("MKO_003_D01","MKO_LIP_003","MAKEOVER_001","D01","Lover","#E08898","cool"),
    ("MKO_003_D02","MKO_LIP_003","MAKEOVER_001","D02","Aura","#D07888","cool"),
    ("MKO_003_D04","MKO_LIP_003","MAKEOVER_001","D04","IYKYK","#C06878","cool"),
    ("MKO_003_D05","MKO_LIP_003","MAKEOVER_001","D05","Candied","#E08070","warm"),
    ("MKO_003_D09","MKO_LIP_003","MAKEOVER_001","D09","Crush","#D05878","cool"),
    ("MKO_003_D14","MKO_LIP_003","MAKEOVER_001","D14","Cherry","#B03040","cool"),
    ("MKO_003_D18","MKO_LIP_003","MAKEOVER_001","D18","Duchess","#C07888","cool"),
    ("MKO_003_D24","MKO_LIP_003","MAKEOVER_001","D24","Velvet","#A03060","cool"),
    # TIMEPHORIA Nebula Velvet
    ("TMP_001_01","TMP_LIP_001","TIMEPHORIA_001","01","Celestial Rose","#D4607A","cool"),
    ("TMP_001_02","TMP_LIP_001","TIMEPHORIA_001","02","Aurora Red","#C02838","neutral"),
    ("TMP_001_03","TMP_LIP_001","TIMEPHORIA_001","03","Nebula Nude","#C49070","warm"),
    ("TMP_001_04","TMP_LIP_001","TIMEPHORIA_001","04","Stardust Mauve","#A06878","cool"),
    ("TMP_001_05","TMP_LIP_001","TIMEPHORIA_001","05","Galaxy Berry","#8B2050","cool"),
    ("TMP_001_06","TMP_LIP_001","TIMEPHORIA_001","06","Cosmic Coral","#D06050","warm"),
    ("TMP_001_07","TMP_LIP_001","TIMEPHORIA_001","07","Supernova Pink","#E07090","cool"),
    ("TMP_001_08","TMP_LIP_001","TIMEPHORIA_001","08","Eclipse Brown","#906050","warm"),
    # TIMEPHORIA Stellar Dust
    ("TMP_002_01","TMP_LIP_002","TIMEPHORIA_001","01","Meteor Pink","#E08898","cool"),
    ("TMP_002_02","TMP_LIP_002","TIMEPHORIA_001","02","Comet Red","#C03040","neutral"),
    ("TMP_002_03","TMP_LIP_002","TIMEPHORIA_001","03","Pulsar Coral","#D07060","warm"),
    # TIMEPHORIA Eternal Lip Matte
    ("TMP_003_01","TMP_LIP_003","TIMEPHORIA_001","01","Eternal Rose","#C06070","cool"),
    ("TMP_003_02","TMP_LIP_003","TIMEPHORIA_001","02","Eternal Red","#B02030","neutral"),
    ("TMP_003_03","TMP_LIP_003","TIMEPHORIA_001","03","Eternal Nude","#C49878","warm"),
    # PIXY Lip Cream
    ("PIX_001_01","PIX_LIP_001","PIXY_001","01","Chic Rose","#D08090","cool"),
    ("PIX_001_02","PIX_LIP_001","PIXY_001","02","Party Red","#C02030","neutral"),
    ("PIX_001_03","PIX_LIP_001","PIXY_001","03","Classic Red","#B01828","neutral"),
    ("PIX_001_04","PIX_LIP_001","PIXY_001","04","Fun Fuchsia","#D03070","cool"),
    ("PIX_001_05","PIX_LIP_001","PIXY_001","05","Edgy Plum","#7A2050","cool"),
    ("PIX_001_06","PIX_LIP_001","PIXY_001","06","Bold Maroon","#901828","cool"),
    ("PIX_001_07","PIX_LIP_001","PIXY_001","08","Delicate Pink","#E09098","cool"),
    ("PIX_001_08","PIX_LIP_001","PIXY_001","09","Sweet Choco","#8B5040","warm"),
    ("PIX_001_09","PIX_LIP_001","PIXY_001","10","Gaudy Orange","#D07040","warm"),
    ("PIX_001_10","PIX_LIP_001","PIXY_001","11","Mild Peach","#E0A080","warm"),
    # PIXY Mousse Moments
    ("PIX_003_01","PIX_LIP_003","PIXY_001","01","Crowd in Red","#C02030","neutral"),
    ("PIX_003_02","PIX_LIP_003","PIXY_001","02","Relaxing Pink","#E08898","cool"),
    ("PIX_003_03","PIX_LIP_003","PIXY_001","03","Peacefully Brown","#B07860","warm"),
    ("PIX_003_04","PIX_LIP_003","PIXY_001","04","Busiest Maroon","#7A1828","cool"),
    ("PIX_003_05","PIX_LIP_003","PIXY_001","05","Calm in Rose","#C08888","neutral"),
    ("PIX_003_06","PIX_LIP_003","PIXY_001","06","Enjoyable Fuchsia","#C83068","cool"),
    # OMG Lip Cream
    ("OMG_001_01","OMG_LIP_001","OMG_001","01","Nude Beige","#C49878","warm"),
    ("OMG_001_02","OMG_LIP_001","OMG_001","02","Pink Petal","#D08090","cool"),
    ("OMG_001_03","OMG_LIP_001","OMG_001","03","Cherry Red","#B02030","neutral"),
    ("OMG_001_04","OMG_LIP_001","OMG_001","04","Brick Brown","#A05040","warm"),
    ("OMG_001_05","OMG_LIP_001","OMG_001","05","Berry Purple","#8B2848","cool"),
    ("OMG_001_06","OMG_LIP_001","OMG_001","06","Coral Orange","#D07058","warm"),
    ("OMG_001_07","OMG_LIP_001","OMG_001","07","Rose Mauve","#B07878","cool"),
    ("OMG_001_08","OMG_LIP_001","OMG_001","08","Dark Maroon","#7A1828","cool"),
    # LATULIPE Matte Lip Cream
    ("LTP_001_01","LTP_LIP_001","LATULIPE_001","01","Rose Nude","#C49080","neutral"),
    ("LTP_001_02","LTP_LIP_001","LATULIPE_001","02","Cherry Blossom","#D07888","cool"),
    ("LTP_001_03","LTP_LIP_001","LATULIPE_001","03","Brick Red","#B04030","warm"),
    ("LTP_001_04","LTP_LIP_001","LATULIPE_001","04","Berry Wine","#8B2040","cool"),
    ("LTP_001_05","LTP_LIP_001","LATULIPE_001","05","Terracotta","#B55840","warm"),
    # LATULIPE True Color
    ("LTP_002_01","LTP_LIP_002","LATULIPE_001","10","Coffee Break","#906050","warm"),
    ("LTP_002_02","LTP_LIP_002","LATULIPE_001","11","Dusty Rose","#C08888","cool"),
    ("LTP_002_03","LTP_LIP_002","LATULIPE_001","12","Classic Red","#C02030","neutral"),
    # LTPRO Lip Glow Oil
    ("LTPR_001_01","LTPR_LIP_001","LTPRO_001","01","Clear Glow","#E0A090","warm"),
    ("LTPR_001_02","LTPR_LIP_001","LTPRO_001","02","Rose Glow","#D08888","cool"),
    ("LTPR_001_03","LTPR_LIP_001","LTPRO_001","03","Berry Glow","#C06878","cool"),
    ("LTPR_001_04","LTPR_LIP_001","LTPRO_001","04","Coral Glow","#D07868","warm"),
    # LTPRO Matte Lip Cream
    ("LTPR_002_01","LTPR_LIP_002","LTPRO_001","01","Nude Mauve","#B08888","neutral"),
    ("LTPR_002_02","LTPR_LIP_002","LTPRO_001","02","Deep Rose","#C06070","cool"),
    ("LTPR_002_03","LTPR_LIP_002","LTPRO_001","03","Burnt Sienna","#A05038","warm"),
    ("LTPR_002_04","LTPR_LIP_002","LTPRO_001","04","Wine Red","#7A1830","cool"),
    # BARENBLISS Cherry Lip Velvet
    ("BNB_001_01","BNB_LIP_001","BARENBLISS_001","01","Sweet Cherry","#C03050","cool"),
    ("BNB_001_02","BNB_LIP_001","BARENBLISS_001","02","Rose Velvet","#D07080","cool"),
    ("BNB_001_03","BNB_LIP_001","BARENBLISS_001","03","Take Chance","#C08070","neutral"),
    ("BNB_001_04","BNB_LIP_001","BARENBLISS_001","07","Nude Brown","#A07060","warm"),
    ("BNB_001_05","BNB_LIP_001","BARENBLISS_001","13","Rise Up","#B03060","cool"),
    # BARENBLISS Peach Liptint
    ("BNB_002_01","BNB_LIP_002","BARENBLISS_001","01","Peach Fuzz","#E09080","warm"),
    ("BNB_002_02","BNB_LIP_002","BARENBLISS_001","02","Peachy Pink","#E08888","cool"),
    ("BNB_002_03","BNB_LIP_002","BARENBLISS_001","03","Coral Peach","#D07868","warm"),
    # BARENBLISS Apple Mousse Tint
    ("BNB_003_01","BNB_LIP_003","BARENBLISS_001","01","Apple Red","#C03040","neutral"),
    ("BNB_003_02","BNB_LIP_003","BARENBLISS_001","02","Apple Rose","#D07888","cool"),
    ("BNB_003_03","BNB_LIP_003","BARENBLISS_001","03","Apple Nude","#C49080","warm"),
    ("BNB_003_04","BNB_LIP_003","BARENBLISS_001","04","Apple Berry","#A02848","cool"),
    # BARENBLISS Vinyl Lip Cream
    ("BNB_004_01","BNB_LIP_004","BARENBLISS_001","01","Vinyl Red","#C02030","neutral"),
    ("BNB_004_02","BNB_LIP_004","BARENBLISS_001","02","Vinyl Rose","#D07888","cool"),
    ("BNB_004_03","BNB_LIP_004","BARENBLISS_001","03","Vinyl Coral","#D07060","warm"),
    # SOMETHINC IDOL Blurry Lip Matte
    ("SMT_001_01","SMT_LIP_001","SOMETHINC_001","BLOW","Blow Nude","#C4906C","warm"),
    ("SMT_001_02","SMT_LIP_001","SOMETHINC_001","GLOW","Glow Pink","#E08898","cool"),
    ("SMT_001_03","SMT_LIP_001","SOMETHINC_001","FLOW","Flow Rose","#C07080","cool"),
    ("SMT_001_04","SMT_LIP_001","SOMETHINC_001","SHOW","Show Red","#C02838","neutral"),
    ("SMT_001_05","SMT_LIP_001","SOMETHINC_001","CROW","Crow Berry","#8B2040","cool"),
    # SOMETHINC Transferproof Lipstick
    ("SMT_002_01","SMT_LIP_002","SOMETHINC_001","04","Grandmaster","#8B3050","cool"),
    ("SMT_002_02","SMT_LIP_002","SOMETHINC_001","07","Cold Cocoa","#906050","warm"),
    ("SMT_002_03","SMT_LIP_002","SOMETHINC_001","01","First Love","#D07888","cool"),
    ("SMT_002_04","SMT_LIP_002","SOMETHINC_001","02","True Red","#C02030","neutral"),
    ("SMT_002_05","SMT_LIP_002","SOMETHINC_001","03","Nude Crush","#C49080","warm"),
]

def hex_to_rgb(h):
    h = h.lstrip('#')
    return int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)

def rgb_to_lab(rgb):
    r,g,b = [x/255.0 for x in rgb]
    def lin(c): return c/12.92 if c<=0.04045 else ((c+0.055)/1.055)**2.4
    r,g,b = lin(r),lin(g),lin(b)
    x=(r*0.4124564+g*0.3575761+b*0.1804375)/0.95047
    y=(r*0.2126729+g*0.7151522+b*0.0721750)/1.00000
    z=(r*0.0193339+g*0.1191920+b*0.9503041)/1.08883
    def f(t): return t**(1/3) if t>0.008856 else 7.787*t+16/116
    fx,fy,fz=f(x),f(y),f(z)
    return round((116*fy)-16,1), round(500*(fx-fy),1), round(200*(fy-fz),1)

def detect_family(h):
    r,g,b = hex_to_rgb(h)
    br = (r+g+b)/3
    if r>180 and g<120 and b<120: return 'pink' if b>100 else 'red'
    if r>160 and g>100 and b<120: return 'coral_orange'
    if r>150 and g<100 and b>80:  return 'berry'
    if r>120 and g<80  and b<80:  return 'deep_red'
    if br>160: return 'nude_light'
    if r>140 and g>100 and b>80:  return 'nude_medium'
    if r>100 and g>60  and b>50:  return 'brown'
    return 'neutral'

def detect_depth(L):
    if L>=65: return 'light'
    if L>=50: return 'medium'
    if L>=35: return 'deep'
    return 'very_deep'

GLOSS_MAP  = {'gloss':85,'glossy_tint':75,'satin':45,'soft_matte':20,
              'tint':30,'velvet_matte':8,'matte':5,'liquid_matte':5}
OPACITY_MAP = {'matte':97,'velvet_matte':95,'soft_matte':88,
               'satin':85,'tint':60,'gloss':80}

def init_db():
    import core.db as db_module
    import core.makeover_inject as mi
    db_module.DB_PATH = DB_PATH
    mi.DB_PATH        = DB_PATH

    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA)

    count = conn.execute("SELECT COUNT(*) FROM brands").fetchone()[0]
    if count >= len(BRANDS):
        print(f"  DB OK - {count} brands already loaded")
        conn.close()
        return

    print("  Inserting embedded data...")
    for b in BRANDS:
        conn.execute("INSERT OR REPLACE INTO brands VALUES (?,?,?,?,?,?)", b)
    for p in PRODUCTS:
        conn.execute("INSERT OR REPLACE INTO products VALUES (?,?,?,?,?,?,?)", p)
    for s in SHADES:
        sid, pid, bid, num, name, hex_c, undertone = s
        r,g,b    = hex_to_rgb(hex_c)
        ll,la,lb = rgb_to_lab((r,g,b))
        family   = detect_family(hex_c)
        depth    = detect_depth(ll)
        prod = conn.execute("SELECT finish FROM products WHERE product_id=?", (pid,)).fetchone()
        finish = prod[0] if prod else 'matte'
        gloss  = GLOSS_MAP.get(finish, 15)
        opac   = OPACITY_MAP.get(finish, 90)
        conn.execute("""
            INSERT OR REPLACE INTO shades
            (shade_id,product_id,brand_id,shade_number,shade_name,hex,
             rgb_r,rgb_g,rgb_b,lab_l,lab_a,lab_b,
             undertone,color_family,depth,opacity,gloss_level,confidence,verified)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (sid,pid,bid,num,name,hex_c,r,g,b,ll,la,lb,
              undertone,family,depth,opac,gloss,78,0))

    conn.commit()
    total = conn.execute("SELECT COUNT(*) FROM shades").fetchone()[0]
    conn.close()
    print(f"  Inserted: {total} shades from {len(BRANDS)} brands")

print("="*50)
print("Opshe Beauty AR SDK")
print(f"DB: {DB_PATH}")
print("="*50)
init_db()

if __name__ == "__main__":
    conn = sqlite3.connect(DB_PATH)
    b = conn.execute("SELECT COUNT(*) FROM brands").fetchone()[0]
    s = conn.execute("SELECT COUNT(*) FROM shades").fetchone()[0]
    conn.close()
    print(f"Brands:{b} Shades:{s}")
    app.run(debug=True, port=5000, host="0.0.0.0")
