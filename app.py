# ============================================================
# BRONX ULTRA OSINT BOT V100 ULTRA ADVANCED
# ============================================================

import telebot
import subprocess
import os
import zipfile
import tempfile
import shutil
from telebot import types
import time
from datetime import datetime, timedelta
import psutil
import sqlite3
import json
import logging
import signal
import threading
import re
import sys
import atexit
import requests
import schedule
import uuid
import random
import string
from flask import Flask, jsonify
from threading import Thread
import hashlib
import base64

# ============================================================
# FLASK KEEP-ALIVE
# ============================================================

app = Flask(__name__)

@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>BRONX ULTRA OSINT BOT V100</title>
        <style>
            body {
                font-family: 'Courier New', monospace;
                background: linear-gradient(135deg, #0a0a0a, #1a0033);
                color: #00ff88;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
                overflow: hidden;
            }
            .container {
                text-align: center;
                padding: 50px;
                border: 2px solid #00ff88;
                border-radius: 20px;
                background: rgba(0,0,0,0.7);
                box-shadow: 0 0 50px rgba(0,255,136,0.3);
                animation: glow 2s ease-in-out infinite alternate;
            }
            @keyframes glow {
                from { box-shadow: 0 0 20px rgba(0,255,136,0.2); }
                to { box-shadow: 0 0 60px rgba(0,255,136,0.6); }
            }
            .title {
                font-size: 48px;
                font-weight: bold;
                background: linear-gradient(45deg, #00ff88, #00ccff);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                animation: rainbow 3s ease-in-out infinite;
            }
            @keyframes rainbow {
                0% { filter: hue-rotate(0deg); }
                100% { filter: hue-rotate(360deg); }
            }
            .status {
                font-size: 24px;
                color: #ffcc00;
                margin: 20px 0;
                animation: blink 1s step-end infinite;
            }
            @keyframes blink {
                50% { opacity: 0; }
            }
            .info {
                color: #aaa;
                font-size: 14px;
                margin-top: 30px;
            }
            .version {
                color: #ff4444;
                font-size: 18px;
                font-weight: bold;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="title">⚡ BRONX ULTRA OSINT</div>
            <div class="version">🔥 V100 ULTRA ADVANCED 🔥</div>
            <div class="status">🤖 BOT IS RUNNING PERFECTLY</div>
            <div style="color: #00ff88; font-size: 20px;">⚡ Response: 10ms (Flash of Light)</div>
            <div style="color: #ff66ff; font-size: 16px;">💾 RAM: 500GB | 📁 Storage: Unlimited</div>
            <div style="color: #66ffcc; font-size: 16px;">🖥️ Hard Disk: 100 Billion</div>
            <div class="info">🚀 Powered by BRONX ULTRA OSINT v21.0</div>
            <div style="margin-top: 20px; color: #666;">
                <span>━━━━━━━━━━━━━━━━━━━━━━━━━</span>
            </div>
        </div>
    </body>
    </html>
    """

@app.route('/status')
def status():
    return jsonify({
        "status": "running",
        "version": "V100 ULTRA",
        "uptime": str(datetime.now() - BOT_START_TIME),
        "users": len(active_users),
        "bots": len(bot_scripts)
    })

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()
    print("🚀 Flask Keep-Alive server started on port 8080")

# ============================================================
# BOT CONFIGURATION
# ============================================================

BOT_START_TIME = datetime.now()

def get_uptime():
    uptime = datetime.now() - BOT_START_TIME
    days = uptime.days
    hours, remainder = divmod(uptime.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{days}d {hours}h {minutes}m {seconds}s"

TOKEN = '8899527443:AAHEoFVC5MdlpCTJ_6wh1HlNIJVyC_FizAE'
OWNER_ID = 6840524720
ADMIN_ID = 6840524720
YOUR_USERNAME = '@BRONX_ULTRA'
UPDATE_CHANNEL = 'https://t.me/bronx_ultra_osint'

# ============================================================
# CHATGPT API
# ============================================================

CHATGPT_API_URL = "https://api.itsrose.life/ai/chatgpt"
CHATGPT_API_KEY = "rose"

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_BOTS_DIR = os.path.join(BASE_DIR, 'upload_bots')
IROTECH_DIR = os.path.join(BASE_DIR, 'inf')
DATABASE_PATH = os.path.join(IROTECH_DIR, 'bot_data.db')

# ============================================================
# LIMITS
# ============================================================

FREE_USER_LIMIT = 1
FREE_USER_HOURS = 24
SUBSCRIBED_USER_LIMIT = 15
ADMIN_LIMIT = 999
OWNER_LIMIT = float('inf')

os.makedirs(UPLOAD_BOTS_DIR, exist_ok=True)
os.makedirs(IROTECH_DIR, exist_ok=True)

bot = telebot.TeleBot(TOKEN)

bot_scripts = {}
user_subscriptions = {}
user_files = {}
active_users = set()
admin_ids = {ADMIN_ID, OWNER_ID}
bot_locked = False
user_hosting = {}
user_ban = {}
user_prime = {}
user_vip = {}
free_user_enabled = True
pending_payments = {}
bot_monitor = {}

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ============================================================
# SUBSCRIPTION PLANS WITH SEPARATE QR CODES
# ============================================================

# 🥇 PRIME PLANS - Separate QR
PRIME_PLANS = {
    "5 Days": {"days": 5, "price": "₹50", "qr": "https://i.ibb.co/mVyp4G45/Screenshot-20260730-144036-1.jpg", "emoji": "🚀"},
    "15 Days": {"days": 15, "price": "₹100", "qr": "https://i.ibb.co/mVyp4G45/Screenshot-20260730-144036-1.jpg", "emoji": "💫"},
    "30 Days": {"days": 30, "price": "₹199", "qr": "https://i.ibb.co/mVyp4G45/Screenshot-20260730-144036-1.jpg", "emoji": "🔥"},
    "40 Days": {"days": 40, "price": "₹240", "qr": "https://i.ibb.co/mVyp4G45/Screenshot-20260730-144036-1.jpg", "emoji": "⚡"},
    "60 Days": {"days": 60, "price": "₹299", "qr": "https://i.ibb.co/mVyp4G45/Screenshot-20260730-144036-1.jpg", "emoji": "💎"},
    "80 Days": {"days": 80, "price": "₹499", "qr": "https://i.ibb.co/mVyp4G45/Screenshot-20260730-144036-1.jpg", "emoji": "👑"},
    "150 Days": {"days": 150, "price": "₹799", "qr": "https://i.ibb.co/mVyp4G45/Screenshot-20260730-144036-1.jpg", "emoji": "🌙"},
    "365 Days": {"days": 365, "price": "₹999", "qr": "https://i.ibb.co/mVyp4G45/Screenshot-20260730-144036-1.jpg", "emoji": "🌟"}
}

# ⭐ VIP PLANS - Separate QR
VIP_PLANS = {
    "30 Days": {"days": 30, "price": "₹300", "qr": "https://i.ibb.co/mVyp4G45/Screenshot-20260730-144036-1.jpg", "emoji": "💜"},
    "60 Days": {"days": 60, "price": "₹600", "qr": "https://i.ibb.co/mVyp4G45/Screenshot-20260730-144036-1.jpg", "emoji": "✨"},
    "80 Days": {"days": 80, "price": "₹800", "qr": "https://i.ibb.co/mVyp4G45/Screenshot-20260730-144036-1.jpg", "emoji": "⭐"},
    "150 Days": {"days": 150, "price": "₹1500", "qr": "https://i.ibb.co/mVyp4G45/Screenshot-20260730-144036-1.jpg", "emoji": "🌌"},
    "200 Days": {"days": 200, "price": "₹2000", "qr": "https://i.ibb.co/mVyp4G45/Screenshot-20260730-144036-1.jpg", "emoji": "🏆"},
    "365 Days": {"days": 365, "price": "₹36500", "qr": "https://i.ibb.co/mVyp4G45/Screenshot-20260730-144036-1.jpg", "emoji": "👑"},
    "Life Time": {"days": 99999, "price": "₹10000", "qr": "https://i.ibb.co/mVyp4G45/Screenshot-20260730-144036-1.jpg", "emoji": "♾️"}
}

# ============================================================
# ULTRA UI - MAIN MENU BUTTONS
# ============================================================

COMMAND_BUTTONS_LAYOUT_USER_SPEC = [
    ["📢 Updates Channel", "⏱ Uptime"],
    ["📤 Upload File", "📂 Check Files"],
    ["⚡ Bot Speed", "📊 Statistics"],
    ["💲 Price List", "📞 Contact Owner"],
    ["🤖 ChatGPT", "🎮 Game Zone"]
]

ADMIN_COMMAND_BUTTONS_LAYOUT_USER_SPEC = [
    ["📢 Updates Channel", "⏱ Uptime"],
    ["📤 Upload File", "📂 Check Files"],
    ["⚡ Bot Speed", "📊 Statistics"],
    ["💳 Subscriptions", "📢 Broadcast"],
    ["🔒 Lock Bot", "🟢 Running All Code"],
    ["👑 Admin Panel", "📞 Contact Owner"],
    ["🤖 ChatGPT", "💲 Price List"],
    ["📂 Global History", "🖥️ Bot Manager"],
    ["📊 System Stats", "🎮 Game Zone"]
]

# ============================================================
# DATABASE INITIALIZATION
# ============================================================

def init_db():
    logger.info(f"Initializing database at: {DATABASE_PATH}")
    try:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS subscriptions
                     (user_id INTEGER PRIMARY KEY, expiry TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS user_files
                     (user_id INTEGER, file_name TEXT, file_type TEXT,
                      PRIMARY KEY (user_id, file_name))''')
        c.execute('''CREATE TABLE IF NOT EXISTS active_users
                     (user_id INTEGER PRIMARY KEY)''')
        c.execute('''CREATE TABLE IF NOT EXISTS admins
                     (user_id INTEGER PRIMARY KEY)''')
        c.execute('''CREATE TABLE IF NOT EXISTS user_hosting
                     (user_id INTEGER PRIMARY KEY, hosting_time TEXT, file_count INTEGER)''')
        c.execute('''CREATE TABLE IF NOT EXISTS user_ban
                     (user_id INTEGER PRIMARY KEY)''')
        c.execute('''CREATE TABLE IF NOT EXISTS user_prime
                     (user_id INTEGER PRIMARY KEY, prime_time TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS user_vip
                     (user_id INTEGER PRIMARY KEY, vip_time TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS global_file_history
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, file_name TEXT, file_type TEXT, upload_time TEXT, file_path TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS free_user_settings
                     (setting_key TEXT PRIMARY KEY, setting_value TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS pending_payments
                     (user_id INTEGER, plan_type TEXT, plan_name TEXT, days INTEGER, price TEXT, timestamp TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS bot_settings
                     (setting_key TEXT PRIMARY KEY, setting_value TEXT)''')
        c.execute('INSERT OR IGNORE INTO admins (user_id) VALUES (?)', (OWNER_ID,))
        if ADMIN_ID != OWNER_ID:
            c.execute('INSERT OR IGNORE INTO admins (user_id) VALUES (?)', (ADMIN_ID,))
        c.execute('INSERT OR IGNORE INTO free_user_settings (setting_key, setting_value) VALUES (?, ?)', 
                  ('file_limit', str(FREE_USER_LIMIT)))
        c.execute('INSERT OR IGNORE INTO free_user_settings (setting_key, setting_value) VALUES (?, ?)', 
                  ('hosting_hours', str(FREE_USER_HOURS)))
        c.execute('INSERT OR IGNORE INTO free_user_settings (setting_key, setting_value) VALUES (?, ?)', 
                  ('enabled', 'True'))
        c.execute('INSERT OR IGNORE INTO bot_settings (setting_key, setting_value) VALUES (?, ?)',
                  ('auto_restart', 'True'))
        conn.commit()
        conn.close()
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error(f"Database initialization error: {e}", exc_info=True)

def load_data():
    logger.info("Loading data from database...")
    try:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()

        c.execute('SELECT user_id, expiry FROM subscriptions')
        for user_id, expiry in c.fetchall():
            try:
                user_subscriptions[user_id] = {'expiry': datetime.fromisoformat(expiry)}
            except ValueError:
                logger.warning(f"Invalid expiry date format for user {user_id}: {expiry}. Skipping.")

        c.execute('SELECT user_id, file_name, file_type FROM user_files')
        for user_id, file_name, file_type in c.fetchall():
            if user_id not in user_files:
                user_files[user_id] = []
            user_files[user_id].append((file_name, file_type))

        c.execute('SELECT user_id FROM active_users')
        active_users.update(user_id for (user_id,) in c.fetchall())

        c.execute('SELECT user_id FROM admins')
        admin_ids.update(user_id for (user_id,) in c.fetchall())

        c.execute('SELECT user_id, hosting_time, file_count FROM user_hosting')
        for user_id, hosting_time, file_count in c.fetchall():
            try:
                user_hosting[user_id] = {'hosting_time': datetime.fromisoformat(hosting_time), 'file_count': file_count}
            except ValueError:
                logger.warning(f"Invalid hosting date format for user {user_id}: {hosting_time}. Skipping.")

        c.execute('SELECT user_id FROM user_ban')
        user_ban.update(user_id for (user_id,) in c.fetchall())

        c.execute('SELECT user_id, prime_time FROM user_prime')
        for user_id, prime_time in c.fetchall():
            try:
                user_prime[user_id] = {'prime_time': datetime.fromisoformat(prime_time)}
            except ValueError:
                logger.warning(f"Invalid prime date format for user {user_id}: {prime_time}. Skipping.")

        c.execute('SELECT user_id, vip_time FROM user_vip')
        for user_id, vip_time in c.fetchall():
            try:
                user_vip[user_id] = {'vip_time': datetime.fromisoformat(vip_time)}
            except ValueError:
                logger.warning(f"Invalid vip date format for user {user_id}: {vip_time}. Skipping.")

        conn.close()
        logger.info(f"Data loaded: {len(active_users)} users, {len(user_subscriptions)} subscriptions, {len(admin_ids)} admins, {len(user_hosting)} hosting, {len(user_ban)} banned, {len(user_prime)} prime, {len(user_vip)} vip.")
    except Exception as e:
        logger.error(f"Error loading data: {e}", exc_info=True)

init_db()
load_data()

# ============================================================
# ULTRA UI FUNCTIONS
# ============================================================

def create_ultra_main_menu(user_id):
    """Ultra Advanced Main Menu with Animations"""
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    # Row 1: Channel & Uptime
    markup.row(
        types.InlineKeyboardButton('📢 Updates', url=UPDATE_CHANNEL),
        types.InlineKeyboardButton('⏱ Uptime', callback_data='uptime')
    )
    
    # Row 2: Upload & Files
    markup.row(
        types.InlineKeyboardButton('📤 Upload File', callback_data='upload'),
        types.InlineKeyboardButton('📂 Check Files', callback_data='check_files')
    )
    
    # Row 3: Speed & Stats
    markup.row(
        types.InlineKeyboardButton('⚡ Bot Speed', callback_data='speed'),
        types.InlineKeyboardButton('📊 Statistics', callback_data='stats')
    )
    
    # Row 4: Price & Contact
    markup.row(
        types.InlineKeyboardButton('💲 Price List', callback_data='price_list'),
        types.InlineKeyboardButton('📞 Contact Owner', url=f'https://t.me/{YOUR_USERNAME.replace("@", "")}')
    )
    
    # Row 5: ChatGPT & Games
    markup.row(
        types.InlineKeyboardButton('🤖 ChatGPT', callback_data='chatgpt'),
        types.InlineKeyboardButton('🎮 Game Zone', callback_data='games')
    )
    
    # Admin Buttons
    if user_id in admin_ids:
        markup.row(
            types.InlineKeyboardButton('💳 Subscriptions', callback_data='subscription'),
            types.InlineKeyboardButton('📢 Broadcast', callback_data='broadcast')
        )
        markup.row(
            types.InlineKeyboardButton('🔒 Lock Bot' if not bot_locked else '🔓 Unlock Bot',
                                     callback_data='lock_bot' if not bot_locked else 'unlock_bot'),
            types.InlineKeyboardButton('🟢 Run All Bots', callback_data='run_all_scripts')
        )
        markup.row(
            types.InlineKeyboardButton('👑 Admin Panel', callback_data='admin_panel'),
            types.InlineKeyboardButton('📂 Global History', callback_data='global_history')
        )
        markup.row(
            types.InlineKeyboardButton('🖥️ Bot Manager', callback_data='bot_manager'),
            types.InlineKeyboardButton('📊 System Stats', callback_data='system_stats')
        )
    
    return markup

def create_reply_keyboard_ultra(user_id):
    """Ultra Reply Keyboard with Modern Style"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    layout_to_use = ADMIN_COMMAND_BUTTONS_LAYOUT_USER_SPEC if user_id in admin_ids else COMMAND_BUTTONS_LAYOUT_USER_SPEC
    for row_buttons_text in layout_to_use:
        markup.add(*[types.KeyboardButton(text) for text in row_buttons_text])
    return markup

# ============================================================
# ULTRA PRICE LIST UI
# ============================================================

def create_ultra_price_list():
    """Ultra Advanced Price List with Animation Styling"""
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    # Prime Section
    markup.row(
        types.InlineKeyboardButton("🥇 PRIME PLANS 🥇", callback_data='show_prime_plans')
    )
    
    # VIP Section
    markup.row(
        types.InlineKeyboardButton("⭐ VIP PLANS ⭐", callback_data='show_vip_plans')
    )
    
    # Contact & Back
    markup.row(
        types.InlineKeyboardButton("📞 Contact Owner", url=f'https://t.me/{YOUR_USERNAME.replace("@", "")}'),
        types.InlineKeyboardButton("🔙 Back to Main", callback_data='back_to_main')
    )
    
    return markup

def show_prime_plans_ultra(chat_id, message_id=None):
    """Show Prime Plans with Ultra UI"""
    text = """╔══════════════════════════════════════╗
║          🥇 PRIME PLANS 🥇            ║
╠══════════════════════════════════════╣
║                                      ║
║  🚀 5 Days     = ₹50                ║
║  💫 15 Days    = ₹100               ║
║  🔥 30 Days    = ₹199               ║
║  ⚡ 40 Days    = ₹240               ║
║  💎 60 Days    = ₹299               ║
║  👑 80 Days    = ₹499               ║
║  🌙 150 Days   = ₹799               ║
║  🌟 365 Days   = ₹999               ║
║                                      ║
╠══════════════════════════════════════╣
║                                      ║
║  🎁 PRIME FEATURES:                 ║
║  ✅ 24/7 Working                     ║
║  ✅ All Time Running                 ║
║  ✅ No Stop                          ║
║  ✅ Fast Response (10ms)             ║
║  ✅ File Hosting Limit               ║
║  ✅ Py, JS, ZIP Support              ║
║  ✅ 500GB RAM                        ║
║  ✅ Unlimited Storage                ║
║                                      ║
╚══════════════════════════════════════╝
    
💡 Select a plan below:"""

    markup = types.InlineKeyboardMarkup(row_width=2)
    for plan_name, plan_data in PRIME_PLANS.items():
        markup.add(types.InlineKeyboardButton(
            f"{plan_data['emoji']} {plan_name} - {plan_data['price']}", 
            callback_data=f'buy_prime_{plan_data["days"]}_{plan_name}'
        ))
    markup.add(types.InlineKeyboardButton("🔙 Back to Price List", callback_data='price_list'))
    
    if message_id:
        try:
            bot.edit_message_text(text, chat_id, message_id, reply_markup=markup, parse_mode='Markdown')
        except:
            bot.send_message(chat_id, text, reply_markup=markup, parse_mode='Markdown')
    else:
        bot.send_message(chat_id, text, reply_markup=markup, parse_mode='Markdown')

def show_vip_plans_ultra(chat_id, message_id=None):
    """Show VIP Plans with Ultra UI"""
    text = """╔══════════════════════════════════════╗
║          ⭐ VIP PLANS ⭐              ║
╠══════════════════════════════════════╣
║                                      ║
║  💜 30 Days     = ₹300              ║
║  ✨ 60 Days     = ₹600              ║
║  ⭐ 80 Days     = ₹800              ║
║  🌌 150 Days    = ₹1500             ║
║  🏆 200 Days    = ₹2000             ║
║  👑 365 Days    = ₹36500            ║
║  ♾️ Life Time   = ₹10000            ║
║                                      ║
╠══════════════════════════════════════╣
║                                      ║
║  🎁 VIP FEATURES:                   ║
║  ✅ Unlimited File Hosting           ║
║  ✅ No Limits                        ║
║  ✅ 24/7 Working                     ║
║  ✅ Ultra Fast Response (5ms)        ║
║  ✅ All Features Unlimited           ║
║  ✅ Any File Support                 ║
║  ✅ 500GB RAM                        ║
║  ✅ Unlimited Storage                ║
║  ✅ Priority Support                 ║
║                                      ║
╚══════════════════════════════════════╝
    
💡 Select a plan below:"""

    markup = types.InlineKeyboardMarkup(row_width=2)
    for plan_name, plan_data in VIP_PLANS.items():
        markup.add(types.InlineKeyboardButton(
            f"{plan_data['emoji']} {plan_name} - {plan_data['price']}", 
            callback_data=f'buy_vip_{plan_data["days"]}_{plan_name}'
        ))
    markup.add(types.InlineKeyboardButton("🔙 Back to Price List", callback_data='price_list'))
    
    if message_id:
        try:
            bot.edit_message_text(text, chat_id, message_id, reply_markup=markup, parse_mode='Markdown')
        except:
            bot.send_message(chat_id, text, reply_markup=markup, parse_mode='Markdown')
    else:
        bot.send_message(chat_id, text, reply_markup=markup, parse_mode='Markdown')

def show_plan_details_ultra(chat_id, message_id, plan_type, plan_name, days, price, qr_url, emoji):
    """Show Plan Details with QR Code"""
    text = f"""╔══════════════════════════════════════╗
║        📝 PLAN SELECTED 📝           ║
╠══════════════════════════════════════╣
║                                      ║
║  {emoji} {plan_type}: {plan_name}       ║
║                                      ║
║  💰 Price: {price}                   ║
║  📅 Duration: {days} days            ║
║                                      ║
╠══════════════════════════════════════╣
║                                      ║"""

    if "PRIME" in plan_type:
        text += """║  🎁 Features:                       ║
║  ✅ 24/7 Working                     ║
║  ✅ All Time Running                 ║
║  ✅ No Stop                          ║
║  ✅ Fast Response (10ms)             ║
║  ✅ File Hosting Limit               ║
║  ✅ Py, JS, ZIP Support              ║
║                                      ║"""
    else:
        text += """║  🎁 Features:                       ║
║  ✅ Unlimited File Hosting           ║
║  ✅ No Limits                        ║
║  ✅ 24/7 Working                     ║
║  ✅ Ultra Fast Response (5ms)        ║
║  ✅ All Features Unlimited           ║
║  ✅ Any File Support                 ║
║  ✅ Priority Support                 ║
║                                      ║"""

    text += f"""╠══════════════════════════════════════╣
║                                      ║
║  📱 Scan QR to Pay:                  ║
║  📞 Contact: {YOUR_USERNAME}          ║
║                                      ║
║  ⚠️ After payment, click             ║
║     "Payment Done" below!            ║
║                                      ║
╚══════════════════════════════════════╝"""

    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.row(
        types.InlineKeyboardButton("✅ Payment Done", callback_data=f'pay_done_{plan_type.lower()}_{days}'),
        types.InlineKeyboardButton("❌ Payment Reject", callback_data='pay_reject')
    )
    markup.row(
        types.InlineKeyboardButton("🔙 Back to Plans", callback_data=f'back_to_{plan_type.lower()}_plans')
    )
    
    try:
        bot.send_photo(chat_id, qr_url, caption=text, reply_markup=markup, parse_mode='Markdown')
        try:
            bot.delete_message(chat_id, message_id)
        except:
            pass
    except Exception as e:
        logger.error(f"Error sending QR: {e}")
        text += f"\n\n🔗 QR Link: {qr_url}"
        try:
            bot.edit_message_text(text, chat_id, message_id, reply_markup=markup, parse_mode='Markdown')
        except:
            bot.send_message(chat_id, text, reply_markup=markup, parse_mode='Markdown')

# ============================================================
# GAME ZONE (New Feature)
# ============================================================

def create_game_zone(chat_id):
    """Game Zone with Fun Games"""
    text = """╔══════════════════════════════════════╗
║          🎮 GAME ZONE 🎮              ║
╠══════════════════════════════════════╣
║                                      ║
║  🎯 Test your luck and skills!       ║
║                                      ║
║  🎰 Spin the Wheel                   ║
║  🎲 Roll the Dice                    ║
║  🃏 Card Game                        ║
║  🔮 Fortune Teller                   ║
║  ⚡ Speed Test                       ║
║                                      ║
╚══════════════════════════════════════╝"""

    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.row(
        types.InlineKeyboardButton("🎰 Spin Wheel", callback_data='spin_wheel'),
        types.InlineKeyboardButton("🎲 Roll Dice", callback_data='roll_dice')
    )
    markup.row(
        types.InlineKeyboardButton("🃏 Card Game", callback_data='card_game'),
        types.InlineKeyboardButton("🔮 Fortune", callback_data='fortune_teller')
    )
    markup.row(
        types.InlineKeyboardButton("⚡ Speed Test", callback_data='speed_test'),
        types.InlineKeyboardButton("🎯 Guess Number", callback_data='guess_number')
    )
    markup.row(
        types.InlineKeyboardButton("🔙 Back to Main", callback_data='back_to_main')
    )
    
    bot.send_message(chat_id, text, reply_markup=markup, parse_mode='Markdown')

def spin_wheel(chat_id):
    """Spin the Wheel Game"""
    prizes = ["🎁 5 Days Prime", "🎁 15 Days Prime", "🎁 30 Days Prime", 
              "🎁 5 Days VIP", "🎁 15 Days VIP", "🎁 30 Days VIP",
              "🎁 10 Free Hours", "🎁 20 Free Hours", "🎁 50 Free Hours",
              "💎 Free Hosting", "🌟 Bonus Files", "🔮 Mystery Gift"]
    
    result = random.choice(prizes)
    emoji = random.choice(["🎉", "🎊", "⭐", "🌟", "💫", "✨", "🎈", "🎁"])
    
    text = f"""╔══════════════════════════════════════╗
║          🎰 WHEEL OF FORTUNE 🎰        ║
╠══════════════════════════════════════╣
║                                      ║
║  🔄 Spinning...                      ║
║                                      ║
║  {emoji} YOU WON: {result} {emoji}     ║
║                                      ║
║  🎊 Congratulations!                 ║
║                                      ║
╚══════════════════════════════════════╝"""

    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("🔄 Spin Again", callback_data='spin_wheel'),
        types.InlineKeyboardButton("🔙 Game Zone", callback_data='games')
    )
    
    bot.send_message(chat_id, text, reply_markup=markup, parse_mode='Markdown')

def roll_dice(chat_id):
    """Roll Dice Game"""
    dice1 = random.randint(1, 6)
    dice2 = random.randint(1, 6)
    total = dice1 + dice2
    
    dice_art = {
        1: "⚀",
        2: "⚁",
        3: "⚂",
        4: "⚃",
        5: "⚄",
        6: "⚅"
    }
    
    text = f"""╔══════════════════════════════════════╗
║          🎲 DICE GAME 🎲              ║
╠══════════════════════════════════════╣
║                                      ║
║  🎲 Dice 1: {dice_art[dice1]} {dice1}           ║
║  🎲 Dice 2: {dice_art[dice2]} {dice2}           ║
║                                      ║
║  📊 Total: {total}                    ║
║                                      ║
║  {'🎉 LUCKY SEVEN!' if total == 7 else '😊 Good Luck!'} ║
║                                      ║
╚══════════════════════════════════════╝"""

    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("🎲 Roll Again", callback_data='roll_dice'),
        types.InlineKeyboardButton("🔙 Game Zone", callback_data='games')
    )
    
    bot.send_message(chat_id, text, reply_markup=markup, parse_mode='Markdown')

def card_game(chat_id):
    """Card Game"""
    suits = ['♠', '♥', '♦', '♣']
    ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
    
    player_card = f"{random.choice(suits)}{random.choice(ranks)}"
    bot_card = f"{random.choice(suits)}{random.choice(ranks)}"
    
    # Simple comparison (A high)
    rank_values = {'A': 14, 'K': 13, 'Q': 12, 'J': 11}
    for i in range(2, 11):
        rank_values[str(i)] = i
    
    p_rank = rank_values[player_card[1:]]
    b_rank = rank_values[bot_card[1:]]
    
    result = "🎉 YOU WIN!" if p_rank > b_rank else "🤖 BOT WINS!" if b_rank > p_rank else "🤝 DRAW!"
    emoji = "🏆" if "WIN" in result else "😅" if "DRAW" in result else "💪"
    
    text = f"""╔══════════════════════════════════════╗
║          🃏 CARD GAME 🃏              ║
╠══════════════════════════════════════╣
║                                      ║
║  🃏 Your Card: {player_card}          ║
║  🤖 Bot Card: {bot_card}             ║
║                                      ║
║  {emoji} {result}                    ║
║                                      ║
╚══════════════════════════════════════╝"""

    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("🃏 Play Again", callback_data='card_game'),
        types.InlineKeyboardButton("🔙 Game Zone", callback_data='games')
    )
    
    bot.send_message(chat_id, text, reply_markup=markup, parse_mode='Markdown')

def fortune_teller(chat_id):
    """Fortune Teller"""
    fortunes = [
        "🌟 Great success awaits you!",
        "💫 A surprise is coming your way!",
        "⭐ Your hard work will pay off!",
        "🌙 Trust your instincts today!",
        "✨ New opportunities are on the horizon!",
        "💎 Someone special is thinking of you!",
        "🎯 You will achieve your goals!",
        "🌈 Good luck is with you!",
        "🔥 Your energy is contagious!",
        "💫 A positive change is coming!"
    ]
    
    result = random.choice(fortunes)
    emoji = random.choice(["🔮", "🌟", "💫", "✨", "⭐", "🌈"])
    
    text = f"""╔══════════════════════════════════════╗
║          🔮 FORTUNE TELLER 🔮         ║
╠══════════════════════════════════════╣
║                                      ║
║  {emoji} {result}                     ║
║                                      ║
║  ✨ The stars have spoken!           ║
║                                      ║
╚══════════════════════════════════════╝"""

    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("🔮 New Fortune", callback_data='fortune_teller'),
        types.InlineKeyboardButton("🔙 Game Zone", callback_data='games')
    )
    
    bot.send_message(chat_id, text, reply_markup=markup, parse_mode='Markdown')

def speed_test(chat_id):
    """Speed Test Game"""
    start_time = time.time()
    text = """╔══════════════════════════════════════╗
║          ⚡ SPEED TEST ⚡             ║
╠══════════════════════════════════════╣
║                                      ║
║  Click the button as fast as you can!║
║                                      ║
╚══════════════════════════════════════╝"""
    
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("⚡ CLICK ME!", callback_data='speed_test_click')
    )
    
    bot.send_message(chat_id, text, reply_markup=markup, parse_mode='Markdown')

def guess_number(chat_id):
    """Guess the Number Game"""
    target = random.randint(1, 10)
    text = """╔══════════════════════════════════════╗
║          🎯 GUESS NUMBER 🎯           ║
╠══════════════════════════════════════╣
║                                      ║
║  Guess a number between 1-10         ║
║  Click a button below!               ║
║                                      ║
╚══════════════════════════════════════╝"""
    
    markup = types.InlineKeyboardMarkup(row_width=5)
    buttons = []
    for i in range(1, 11):
        buttons.append(types.InlineKeyboardButton(str(i), callback_data=f'guess_{i}'))
    markup.row(*buttons[:5])
    markup.row(*buttons[5:])
    markup.row(types.InlineKeyboardButton("🔙 Game Zone", callback_data='games'))
    
    bot.send_message(chat_id, text, reply_markup=markup, parse_mode='Markdown')

def handle_guess(chat_id, user_id, guess):
    """Handle Guess Number"""
    target = random.randint(1, 10)
    if guess == target:
        result = f"🎉 CORRECT! The number was {target}! 🎉"
        emoji = "🏆"
    else:
        result = f"❌ Wrong! The number was {target}. Try again! 🎯"
        emoji = "💪"
    
    text = f"""╔══════════════════════════════════════╗
║          🎯 GUESS NUMBER 🎯           ║
╠══════════════════════════════════════╣
║                                      ║
║  Your Guess: {guess}                  ║
║  Target: {target}                     ║
║                                      ║
║  {emoji} {result}                    ║
║                                      ║
╚══════════════════════════════════════╝"""
    
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("🔄 Play Again", callback_data='guess_number'),
        types.InlineKeyboardButton("🔙 Game Zone", callback_data='games')
    )
    
    bot.send_message(chat_id, text, reply_markup=markup, parse_mode='Markdown')

# ============================================================
# CHATGPT FUNCTIONS
# ============================================================

def chatgpt_query(query):
    """Send query to free ChatGPT API"""
    try:
        headers = {
            "Authorization": CHATGPT_API_KEY,
            "Content-Type": "application/json"
        }
        payload = {
            "query": query
        }
        response = requests.post(CHATGPT_API_URL, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status'):
                return data.get('result', 'No response from ChatGPT')
            else:
                return f"❌ API Error: {data.get('message', 'Unknown error')}"
        else:
            return fallback_chatgpt(query)
    except Exception as e:
        logger.error(f"ChatGPT error: {e}")
        return fallback_chatgpt(query)

def fallback_chatgpt(query):
    """Fallback ChatGPT API"""
    try:
        url = "https://api.popcat.xyz/chatgpt"
        params = {"prompt": query}
        response = requests.get(url, params=params, timeout=30)
        if response.status_code == 200:
            data = response.json()
            return data.get('response', 'No response from API')
        return "❌ ChatGPT is temporarily unavailable. Please try again later."
    except Exception as e:
        logger.error(f"Fallback ChatGPT error: {e}")
        return "❌ ChatGPT is temporarily unavailable. Please try again later."

# ============================================================
# HELPERS FOR BOT SCRIPTS
# ============================================================

def get_free_user_settings():
    conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute('SELECT setting_key, setting_value FROM free_user_settings')
    settings = {key: value for key, value in c.fetchall()}
    conn.close()
    return settings

def get_bot_settings():
    conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute('SELECT setting_key, setting_value FROM bot_settings')
    settings = {key: value for key, value in c.fetchall()}
    conn.close()
    return settings

def get_user_folder(user_id):
    user_folder = os.path.join(UPLOAD_BOTS_DIR, str(user_id))
    os.makedirs(user_folder, exist_ok=True)
    return user_folder

def get_user_file_limit(user_id):
    if user_id == OWNER_ID: return OWNER_LIMIT
    if user_id in admin_ids: return ADMIN_LIMIT
    if user_id in user_vip:
        vip_time = user_vip[user_id].get('vip_time')
        if vip_time and vip_time > datetime.now():
            return float('inf')
    if user_id in user_subscriptions and user_subscriptions[user_id]['expiry'] > datetime.now():
        return SUBSCRIBED_USER_LIMIT
    
    settings = get_free_user_settings()
    if settings.get('enabled', 'True').lower() == 'true':
        return int(settings.get('file_limit', '1'))
    return 0

def get_user_file_count(user_id):
    return len(user_files.get(user_id, []))

def can_user_host(user_id):
    if user_id in user_vip:
        vip_time = user_vip[user_id].get('vip_time')
        if vip_time and vip_time > datetime.now():
            return True
    if user_id in user_prime:
        prime_time = user_prime[user_id].get('prime_time')
        if prime_time and prime_time > datetime.now():
            return True
    if user_id in user_hosting:
        hosting_time = user_hosting[user_id].get('hosting_time')
        if hosting_time and hosting_time > datetime.now():
            return True
    settings = get_free_user_settings()
    if settings.get('enabled', 'True').lower() == 'true':
        return True
    return False

# ============================================================
# BOT MONITORING
# ============================================================

def is_bot_running(script_owner_id, file_name):
    script_key = f"{script_owner_id}_{file_name}"
    script_info = bot_scripts.get(script_key)
    if script_info and script_info.get('process'):
        try:
            proc = psutil.Process(script_info['process'].pid)
            is_running = proc.is_running() and proc.status() != psutil.STATUS_ZOMBIE
            if not is_running:
                if 'log_file' in script_info and hasattr(script_info['log_file'], 'close') and not script_info['log_file'].closed:
                    try:
                        script_info['log_file'].close()
                    except Exception as log_e:
                        logger.error(f"Error closing log file during zombie cleanup {script_key}: {log_e}")
                if script_key in bot_scripts:
                    del bot_scripts[script_key]
            return is_running
        except psutil.NoSuchProcess:
            if 'log_file' in script_info and hasattr(script_info['log_file'], 'close') and not script_info['log_file'].closed:
                try:
                    script_info['log_file'].close()
                except Exception as log_e:
                    logger.error(f"Error closing log file during cleanup of non-existent process {script_key}: {log_e}")
            if script_key in bot_scripts:
                del bot_scripts[script_key]
            return False
        except Exception as e:
            logger.error(f"Error checking process status for {script_key}: {e}", exc_info=True)
            return False
    return False

def kill_process_tree(process_info):
    pid = None
    log_file_closed = False
    script_key = process_info.get('script_key', 'N/A')

    try:
        if 'log_file' in process_info and hasattr(process_info['log_file'], 'close') and not process_info['log_file'].closed:
            try:
                process_info['log_file'].close()
                log_file_closed = True
                logger.info(f"Closed log file for {script_key} (PID: {process_info.get('process', {}).get('pid', 'N/A')})")
            except Exception as log_e:
                logger.error(f"Error closing log file during kill for {script_key}: {log_e}")

        process = process_info.get('process')
        if process and hasattr(process, 'pid'):
            pid = process.pid
            if pid:
                try:
                    parent = psutil.Process(pid)
                    children = parent.children(recursive=True)
                    logger.info(f"Attempting to kill process tree for {script_key} (PID: {pid}, Children: {[c.pid for c in children]})")

                    for child in children:
                        try:
                            child.terminate()
                            logger.info(f"Terminated child process {child.pid} for {script_key}")
                        except psutil.NoSuchProcess:
                            logger.warning(f"Child process {child.pid} for {script_key} already gone.")
                        except Exception as e:
                            logger.error(f"Error terminating child {child.pid} for {script_key}: {e}. Trying kill...")
                            try: child.kill(); logger.info(f"Killed child process {child.pid} for {script_key}")
                            except Exception as e2: logger.error(f"Failed to kill child {child.pid} for {script_key}: {e2}")

                    gone, alive = psutil.wait_procs(children, timeout=1)
                    for p in alive:
                        logger.warning(f"Child process {p.pid} for {script_key} still alive. Killing.")
                        try: p.kill()
                        except Exception as e: logger.error(f"Failed to kill child {p.pid} for {script_key} after wait: {e}")

                    try:
                        parent.terminate()
                        logger.info(f"Terminated parent process {pid} for {script_key}")
                        try: parent.wait(timeout=1)
                        except psutil.TimeoutExpired:
                            logger.warning(f"Parent process {pid} for {script_key} did not terminate. Killing.")
                            parent.kill()
                            logger.info(f"Killed parent process {pid} for {script_key}")
                    except psutil.NoSuchProcess:
                        logger.warning(f"Parent process {pid} for {script_key} already gone.")
                    except Exception as e:
                        logger.error(f"Error terminating parent {pid} for {script_key}: {e}. Trying kill...")
                        try: parent.kill(); logger.info(f"Killed parent process {pid} for {script_key}")
                        except Exception as e2: logger.error(f"Failed to kill parent {pid} for {script_key}: {e2}")

                except psutil.NoSuchProcess:
                    logger.warning(f"Process {pid or 'N/A'} for {script_key} not found during kill. Already terminated?")
            else: logger.error(f"Process PID is None for {script_key}.")
        elif log_file_closed: logger.warning(f"Process object missing for {script_key}, but log file closed.")
        else: logger.error(f"Process object missing for {script_key}, and no log file. Cannot kill.")
    except Exception as e:
        logger.error(f"Unexpected error killing process tree for PID {pid or 'N/A'} ({script_key}): {e}", exc_info=True)

def get_file_content(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {e}")
        return None

def get_last_log_lines(log_path, lines=20):
    try:
        if not os.path.exists(log_path):
            return "No log file found"
        with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
            all_lines = f.readlines()
            last_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
            return ''.join(last_lines)
    except Exception as e:
        return f"Error reading log: {e}"

# ============================================================
# RUN SCRIPT FUNCTIONS
# ============================================================

def run_script(script_path, script_owner_id, user_folder, file_name, message_obj_for_reply, attempt=1):
    max_attempts = 2
    if attempt > max_attempts:
        bot.reply_to(message_obj_for_reply, f"❌ Failed to run '{file_name}' after {max_attempts} attempts. Check logs.")
        return

    script_key = f"{script_owner_id}_{file_name}"
    logger.info(f"Attempt {attempt} to run Python script: {script_path} (Key: {script_key}) for user {script_owner_id}")

    if not can_user_host(script_owner_id):
        bot.reply_to(message_obj_for_reply, "⏰ Your hosting time has expired! Please contact admin.")
        return

    try:
        if not os.path.exists(script_path):
             bot.reply_to(message_obj_for_reply, f"❌ Script '{file_name}' not found!")
             logger.error(f"Script not found: {script_path} for user {script_owner_id}")
             if script_owner_id in user_files:
                 user_files[script_owner_id] = [f for f in user_files.get(script_owner_id, []) if f[0] != file_name]
             remove_user_file_db(script_owner_id, file_name)
             return

        log_file_path = os.path.join(user_folder, f"{os.path.splitext(file_name)[0]}.log")
        log_file = None
        process = None
        
        try:
            log_file = open(log_file_path, 'w', encoding='utf-8', errors='ignore', buffering=1)
        except Exception as e:
            logger.error(f"Failed to open log file '{log_file_path}' for {script_key}: {e}", exc_info=True)
            bot.reply_to(message_obj_for_reply, f"❌ Failed to open log file '{log_file_path}': {e}")
            return

        env = os.environ.copy()
        env['PYTHONPATH'] = user_folder + os.pathsep + env.get('PYTHONPATH', '')
        env['PYTHONUNBUFFERED'] = '1'
        env['PYTHONIOENCODING'] = 'utf-8'

        try:
            startupinfo = None
            creationflags = 0
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
                creationflags = subprocess.CREATE_NO_WINDOW

            if sys.platform == 'win32':
                creationflags = subprocess.CREATE_NO_WINDOW | subprocess.CREATE_NEW_PROCESS_GROUP

            process = subprocess.Popen(
                [sys.executable, script_path],
                cwd=user_folder,
                stdout=log_file,
                stderr=subprocess.STDOUT,
                stdin=subprocess.DEVNULL,
                startupinfo=startupinfo,
                creationflags=creationflags if sys.platform == 'win32' else 0,
                encoding='utf-8',
                errors='ignore',
                close_fds=True,
                shell=False,
                env=env
            )

            time.sleep(3)

            if process.poll() is None:
                logger.info(f"✅ Started Python process {process.pid} for {script_key}")
                
                bot_scripts[script_key] = {
                    'process': process,
                    'log_file': log_file,
                    'file_name': file_name,
                    'chat_id': message_obj_for_reply.chat.id,
                    'script_owner_id': script_owner_id,
                    'start_time': datetime.now(),
                    'user_folder': user_folder,
                    'type': 'py',
                    'script_key': script_key,
                    'log_path': log_file_path
                }
                
                bot.reply_to(message_obj_for_reply, 
                            f"✅ **Script Started Successfully!**\n\n"
                            f"📁 File: `{file_name}`\n"
                            f"🆔 PID: `{process.pid}`\n"
                            f"👤 User: `{script_owner_id}`\n\n"
                            f"⚡ Response Time: 10ms (Flash of Light ⚡)\n"
                            f"💾 RAM: 500GB\n"
                            f"📁 Storage: Unlimited\n"
                            f"💿 Disk: 20 Billion\n"
                            f"🖥️ Hard Disk: 100 Billion\n\n"
                            f"📜 Check logs using control buttons!")
                
                threading.Thread(target=monitor_bot_live, args=(script_key, process, log_file_path, file_name, script_owner_id), daemon=True).start()
                
            else:
                error_code = process.poll()
                logger.error(f"❌ Process {script_key} crashed immediately! Return code: {error_code}")
                
                log_content = get_last_log_lines(log_file_path, 20)
                
                error_hint = ""
                if "ModuleNotFoundError" in log_content or "ImportError" in log_content:
                    error_hint = "\n🔧 **Missing Module!** Try installing dependencies."
                elif "SyntaxError" in log_content:
                    error_hint = "\n🔧 **Syntax Error!** Check your code."
                elif "PermissionError" in log_content:
                    error_hint = "\n🔧 **Permission Error!** Check file permissions."
                elif "Address already in use" in log_content:
                    error_hint = "\n🔧 **Port in use!** Try a different port."
                elif "Invalid token" in log_content:
                    error_hint = "\n🔧 **Invalid Bot Token!** Check your TOKEN."
                
                bot.reply_to(message_obj_for_reply, 
                            f"❌ **Script Crashed Immediately!**\n\n"
                            f"📁 File: `{file_name}`\n"
                            f"🆔 PID: {process.pid}\n"
                            f"💀 Return Code: {error_code}\n\n"
                            f"📜 **Last Log Lines:**\n```\n{log_content[:1500]}\n```\n{error_hint}")
                
                if log_file and not log_file.closed:
                    log_file.close()
                if script_key in bot_scripts:
                    del bot_scripts[script_key]
                return

        except FileNotFoundError:
            logger.error(f"Python interpreter {sys.executable} not found for long run {script_key}")
            bot.reply_to(message_obj_for_reply, f"❌ Python interpreter '{sys.executable}' not found.")
            if log_file and not log_file.closed:
                log_file.close()
            if script_key in bot_scripts:
                del bot_scripts[script_key]
        except Exception as e:
            if log_file and not log_file.closed:
                log_file.close()
            error_msg = f"❌ Error starting Python script '{file_name}': {str(e)}"
            logger.error(error_msg, exc_info=True)
            bot.reply_to(message_obj_for_reply, error_msg)
            
            if process and process.poll() is None:
                logger.warning(f"Killing potentially started Python process {process.pid} for {script_key}")
                kill_process_tree({'process': process, 'log_file': log_file, 'script_key': script_key})
            if script_key in bot_scripts:
                del bot_scripts[script_key]

    except Exception as e:
        error_msg = f"❌ Unexpected error running Python script '{file_name}': {str(e)}"
        logger.error(error_msg, exc_info=True)
        bot.reply_to(message_obj_for_reply, error_msg)
        
        if script_key in bot_scripts:
            logger.warning(f"Cleaning up {script_key} due to error in run_script.")
            kill_process_tree(bot_scripts[script_key])
            del bot_scripts[script_key]

def monitor_bot_live(script_key, process, log_path, file_name, user_id):
    try:
        time.sleep(10)
        
        if script_key not in bot_scripts:
            logger.info(f"Bot {script_key} already removed from tracking")
            return
        
        if process.poll() is not None:
            error_code = process.poll()
            log_content = get_last_log_lines(log_path, 15)
            
            logger.error(f"❌ Bot {script_key} died! Return code: {error_code}")
            
            bot.send_message(OWNER_ID,
                f"❌ **Bot Crashed!**\n\n"
                f"📁 File: `{file_name}`\n"
                f"👤 User: `{user_id}`\n"
                f"💀 Return Code: {error_code}\n\n"
                f"📜 **Last Logs:**\n```\n{log_content[:1500]}\n```")
            
            if script_key in bot_scripts:
                del bot_scripts[script_key]
            return
        
        bot.send_message(OWNER_ID,
            f"✅ **Bot Running Successfully!**\n\n"
            f"📁 File: `{file_name}`\n"
            f"👤 User: `{user_id}`\n"
            f"🆔 PID: {process.pid}\n\n"
            f"⚡ Response Time: 10ms\n"
            f"💾 RAM: 500GB\n"
            f"📁 Storage: Unlimited")
        
        while script_key in bot_scripts:
            try:
                proc = psutil.Process(process.pid)
                if not proc.is_running() or proc.status() == psutil.STATUS_ZOMBIE:
                    log_content = get_last_log_lines(log_path, 15)
                    
                    bot.send_message(OWNER_ID,
                        f"❌ **Bot Crashed!**\n\n"
                        f"📁 File: `{file_name}`\n"
                        f"👤 User: `{user_id}`\n"
                        f"⏱ Uptime: {int((datetime.now() - bot_scripts[script_key]['start_time']).total_seconds())}s\n\n"
                        f"📜 **Last Logs:**\n```\n{log_content[:1500]}\n```")
                    
                    if script_key in bot_scripts:
                        del bot_scripts[script_key]
                    break
                time.sleep(30)
            except psutil.NoSuchProcess:
                log_content = get_last_log_lines(log_path, 15)
                bot.send_message(OWNER_ID,
                    f"❌ **Bot Process Lost!**\n\n"
                    f"📁 File: `{file_name}`\n"
                    f"👤 User: `{user_id}`\n\n"
                    f"📜 **Last Logs:**\n```\n{log_content[:1500]}\n```")
                if script_key in bot_scripts:
                    del bot_scripts[script_key]
                break
            except Exception as e:
                logger.error(f"Monitor error for {script_key}: {e}")
                time.sleep(30)
                
    except Exception as e:
        logger.error(f"Error in monitor_bot_live for {script_key}: {e}")

# ============================================================
# FILE UPLOAD HANDLING
# ============================================================

def handle_zip_file(downloaded_file_content, file_name_zip, message):
    user_id = message.from_user.id
    user_folder = get_user_folder(user_id)
    temp_dir = None
    try:
        temp_dir = tempfile.mkdtemp(prefix=f"user_{user_id}_zip_")
        logger.info(f"Temp dir for zip: {temp_dir}")
        zip_path = os.path.join(temp_dir, file_name_zip)
        with open(zip_path, 'wb') as new_file: new_file.write(downloaded_file_content)
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            for member in zip_ref.infolist():
                member_path = os.path.abspath(os.path.join(temp_dir, member.filename))
                if not member_path.startswith(os.path.abspath(temp_dir)):
                    raise zipfile.BadZipFile(f"Zip has unsafe path: {member.filename}")
            zip_ref.extractall(temp_dir)
            logger.info(f"Extracted zip to {temp_dir}")

        extracted_items = os.listdir(temp_dir)
        py_files = [f for f in extracted_items if f.endswith('.py')]
        js_files = [f for f in extracted_items if f.endswith('.js')]
        req_file = 'requirements.txt' if 'requirements.txt' in extracted_items else None
        pkg_json = 'package.json' if 'package.json' in extracted_items else None

        if req_file:
            req_path = os.path.join(temp_dir, req_file)
            logger.info(f"requirements.txt found, installing: {req_path}")
            bot.reply_to(message, f"📦 Installing Python deps from `{req_file}`...")
            try:
                command = [sys.executable, '-m', 'pip', 'install', '-r', req_path]
                result = subprocess.run(command, capture_output=True, text=True, check=True, encoding='utf-8', errors='ignore')
                logger.info(f"pip install from requirements.txt OK. Output:\n{result.stdout}")
                bot.reply_to(message, f"✅ Python deps from `{req_file}` installed.")
            except subprocess.CalledProcessError as e:
                error_msg = f"❌ Failed to install Python deps from `{req_file}`.\nLog:\n```\n{e.stderr or e.stdout}\n```"
                logger.error(error_msg)
                if len(error_msg) > 4000: error_msg = error_msg[:4000] + "\n... (Log truncated)"
                bot.reply_to(message, error_msg, parse_mode='Markdown'); return
            except Exception as e:
                 error_msg = f"❌ Unexpected error installing Python deps: {e}"
                 logger.error(error_msg, exc_info=True); bot.reply_to(message, error_msg); return

        if pkg_json:
            logger.info(f"package.json found, npm install in: {temp_dir}")
            bot.reply_to(message, f"📦 Installing Node deps from `{pkg_json}`...")
            try:
                command = ['npm', 'install']
                result = subprocess.run(command, capture_output=True, text=True, check=True, cwd=temp_dir, encoding='utf-8', errors='ignore')
                logger.info(f"npm install OK. Output:\n{result.stdout}")
                bot.reply_to(message, f"✅ Node deps from `{pkg_json}` installed.")
            except FileNotFoundError:
                bot.reply_to(message, "❌ 'npm' not found. Cannot install Node deps."); return
            except subprocess.CalledProcessError as e:
                error_msg = f"❌ Failed to install Node deps from `{pkg_json}`.\nLog:\n```\n{e.stderr or e.stdout}\n```"
                logger.error(error_msg)
                if len(error_msg) > 4000: error_msg = error_msg[:4000] + "\n... (Log truncated)"
                bot.reply_to(message, error_msg, parse_mode='Markdown'); return
            except Exception as e:
                 error_msg = f"❌ Unexpected error installing Node deps: {e}"
                 logger.error(error_msg, exc_info=True); bot.reply_to(message, error_msg); return

        main_script_name = None; file_type = None
        preferred_py = ['main.py', 'bot.py', 'app.py']; preferred_js = ['index.js', 'main.js', 'bot.js', 'app.js']
        for p in preferred_py:
            if p in py_files: main_script_name = p; file_type = 'py'; break
        if not main_script_name:
             for p in preferred_js:
                 if p in js_files: main_script_name = p; file_type = 'js'; break
        if not main_script_name:
            if py_files: main_script_name = py_files[0]; file_type = 'py'
            elif js_files: main_script_name = js_files[0]; file_type = 'js'
        if not main_script_name:
            bot.reply_to(message, "❌ No `.py` or `.js` script found in archive!"); return

        logger.info(f"Moving extracted files from {temp_dir} to {user_folder}")
        moved_count = 0
        for item_name in os.listdir(temp_dir):
            src_path = os.path.join(temp_dir, item_name)
            dest_path = os.path.join(user_folder, item_name)
            if os.path.isdir(dest_path): shutil.rmtree(dest_path)
            elif os.path.exists(dest_path): os.remove(dest_path)
            shutil.move(src_path, dest_path); moved_count +=1
        logger.info(f"Moved {moved_count} items to {user_folder}")

        save_user_file(user_id, main_script_name, file_type)
        logger.info(f"Saved main script '{main_script_name}' ({file_type}) for {user_id} from zip.")
        main_script_path = os.path.join(user_folder, main_script_name)
        bot.reply_to(message, f"📁 Files extracted. Starting main script: `{main_script_name}`...", parse_mode='Markdown')

        if file_type == 'py':
             threading.Thread(target=run_script, args=(main_script_path, user_id, user_folder, main_script_name, message)).start()
        elif file_type == 'js':
             threading.Thread(target=run_js_script, args=(main_script_path, user_id, user_folder, main_script_name, message)).start()

    except zipfile.BadZipFile as e:
        logger.error(f"Bad zip file from {user_id}: {e}")
        bot.reply_to(message, f"❌ Invalid/corrupted ZIP. {e}")
    except Exception as e:
        logger.error(f"Error processing zip for {user_id}: {e}", exc_info=True)
        bot.reply_to(message, f"❌ Error processing zip: {str(e)}")
    finally:
        if temp_dir and os.path.exists(temp_dir):
            try: shutil.rmtree(temp_dir); logger.info(f"Cleaned temp dir: {temp_dir}")
            except Exception as e: logger.error(f"Failed to clean temp dir {temp_dir}: {e}", exc_info=True)

# ============================================================
# DATABASE FUNCTIONS
# ============================================================

DB_LOCK = threading.Lock()

def save_user_file(user_id, file_name, file_type='py'):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            c.execute('INSERT OR REPLACE INTO user_files (user_id, file_name, file_type) VALUES (?, ?, ?)',
                      (user_id, file_name, file_type))
            conn.commit()
            if user_id not in user_files: user_files[user_id] = []
            user_files[user_id] = [(fn, ft) for fn, ft in user_files[user_id] if fn != file_name]
            user_files[user_id].append((file_name, file_type))
            logger.info(f"Saved file '{file_name}' ({file_type}) for user {user_id}")
        except sqlite3.Error as e: logger.error(f"SQLite error saving file for user {user_id}, {file_name}: {e}")
        except Exception as e: logger.error(f"Unexpected error saving file for {user_id}, {file_name}: {e}", exc_info=True)
        finally: conn.close()

def remove_user_file_db(user_id, file_name):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            c.execute('DELETE FROM user_files WHERE user_id = ? AND file_name = ?', (user_id, file_name))
            conn.commit()
            if user_id in user_files:
                user_files[user_id] = [f for f in user_files[user_id] if f[0] != file_name]
                if not user_files[user_id]: del user_files[user_id]
            logger.info(f"Removed file '{file_name}' for user {user_id} from DB")
        except sqlite3.Error as e: logger.error(f"SQLite error removing file for {user_id}, {file_name}: {e}")
        except Exception as e: logger.error(f"Unexpected error removing file for {user_id}, {file_name}: {e}", exc_info=True)
        finally: conn.close()

def add_active_user(user_id):
    active_users.add(user_id)
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            c.execute('INSERT OR IGNORE INTO active_users (user_id) VALUES (?)', (user_id,))
            conn.commit()
            logger.info(f"Added/Confirmed active user {user_id} in DB")
        except sqlite3.Error as e: logger.error(f"SQLite error adding active user {user_id}: {e}")
        except Exception as e: logger.error(f"Unexpected error adding active user {user_id}: {e}", exc_info=True)
        finally: conn.close()

def save_subscription(user_id, expiry):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            expiry_str = expiry.isoformat()
            c.execute('INSERT OR REPLACE INTO subscriptions (user_id, expiry) VALUES (?, ?)', (user_id, expiry_str))
            conn.commit()
            user_subscriptions[user_id] = {'expiry': expiry}
            logger.info(f"Saved subscription for {user_id}, expiry {expiry_str}")
        except sqlite3.Error as e: logger.error(f"SQLite error saving subscription for {user_id}: {e}")
        except Exception as e: logger.error(f"Unexpected error saving subscription for {user_id}: {e}", exc_info=True)
        finally: conn.close()

def remove_subscription_db(user_id):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            c.execute('DELETE FROM subscriptions WHERE user_id = ?', (user_id,))
            conn.commit()
            if user_id in user_subscriptions: del user_subscriptions[user_id]
            logger.info(f"Removed subscription for {user_id} from DB")
        except sqlite3.Error as e: logger.error(f"SQLite error removing subscription for {user_id}: {e}")
        except Exception as e: logger.error(f"Unexpected error removing subscription for {user_id}: {e}", exc_info=True)
        finally: conn.close()

def add_admin_db(admin_id):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            c.execute('INSERT OR IGNORE INTO admins (user_id) VALUES (?)', (admin_id,))
            conn.commit()
            admin_ids.add(admin_id)
            logger.info(f"Added admin {admin_id} to DB")
        except sqlite3.Error as e: logger.error(f"SQLite error adding admin {admin_id}: {e}")
        except Exception as e: logger.error(f"Unexpected error adding admin {admin_id}: {e}", exc_info=True)
        finally: conn.close()

def remove_admin_db(admin_id):
    if admin_id == OWNER_ID:
        logger.warning("Attempted to remove OWNER_ID from admins.")
        return False
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        removed = False
        try:
            c.execute('SELECT 1 FROM admins WHERE user_id = ?', (admin_id,))
            if c.fetchone():
                c.execute('DELETE FROM admins WHERE user_id = ?', (admin_id,))
                conn.commit()
                removed = c.rowcount > 0
                if removed: admin_ids.discard(admin_id); logger.info(f"Removed admin {admin_id} from DB")
                else: logger.warning(f"Admin {admin_id} found but delete affected 0 rows.")
            else:
                logger.warning(f"Admin {admin_id} not found in DB.")
                admin_ids.discard(admin_id)
            return removed
        except sqlite3.Error as e: logger.error(f"SQLite error removing admin {admin_id}: {e}"); return False
        except Exception as e: logger.error(f"Unexpected error removing admin {admin_id}: {e}", exc_info=True); return False
        finally: conn.close()

# ============================================================
# CONTROL BUTTONS
# ============================================================

def create_control_buttons(script_owner_id, file_name, is_running=True):
    markup = types.InlineKeyboardMarkup(row_width=2)
    if is_running:
        markup.row(
            types.InlineKeyboardButton("🔴 Stop", callback_data=f'stop_{script_owner_id}_{file_name}'),
            types.InlineKeyboardButton("🔄 Restart", callback_data=f'restart_{script_owner_id}_{file_name}')
        )
        markup.row(
            types.InlineKeyboardButton("🗑️ Delete", callback_data=f'delete_{script_owner_id}_{file_name}'),
            types.InlineKeyboardButton("📜 Logs", callback_data=f'logs_{script_owner_id}_{file_name}')
        )
        markup.row(
            types.InlineKeyboardButton("📄 View Code", callback_data=f'code_{script_owner_id}_{file_name}')
        )
    else:
        markup.row(
            types.InlineKeyboardButton("🟢 Start", callback_data=f'start_{script_owner_id}_{file_name}'),
            types.InlineKeyboardButton("🗑️ Delete", callback_data=f'delete_{script_owner_id}_{file_name}')
        )
        markup.row(
            types.InlineKeyboardButton("📜 View Logs", callback_data=f'logs_{script_owner_id}_{file_name}'),
            types.InlineKeyboardButton("📄 View Code", callback_data=f'code_{script_owner_id}_{file_name}')
        )
    markup.add(types.InlineKeyboardButton("🔙 Back to Files", callback_data='check_files'))
    return markup

# ============================================================
# ADMIN PANEL
# ============================================================

def create_admin_panel():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.row(
        types.InlineKeyboardButton('➕ Add Admin', callback_data='add_admin'),
        types.InlineKeyboardButton('➖ Remove Admin', callback_data='remove_admin')
    )
    markup.row(types.InlineKeyboardButton('📋 List Admins', callback_data='list_admins'))
    markup.row(types.InlineKeyboardButton('⚙️ Free Settings', callback_data='free_settings'))
    markup.row(types.InlineKeyboardButton('📂 Global History', callback_data='global_history'))
    markup.row(types.InlineKeyboardButton('🖥️ Bot Manager', callback_data='bot_manager'))
    markup.row(types.InlineKeyboardButton('📊 System Stats', callback_data='system_stats'))
    markup.row(types.InlineKeyboardButton('👥 All Users Bots', callback_data='all_users_bots'))
    markup.row(types.InlineKeyboardButton('🔙 Back to Main', callback_data='back_to_main'))
    return markup

def create_bot_manager():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.row(
        types.InlineKeyboardButton('📋 List All Bots', callback_data='list_all_bots'),
        types.InlineKeyboardButton('🔄 Auto-Restart Toggle', callback_data='toggle_auto_restart')
    )
    markup.row(
        types.InlineKeyboardButton('📊 System Stats', callback_data='system_stats'),
        types.InlineKeyboardButton('🗑️ Clean Dead Bots', callback_data='clean_dead_bots')
    )
    markup.row(types.InlineKeyboardButton('🔙 Back to Admin', callback_data='admin_panel'))
    return markup

def create_subscription_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.row(
        types.InlineKeyboardButton('➕ Add Subscription', callback_data='add_subscription'),
        types.InlineKeyboardButton('➖ Remove Subscription', callback_data='remove_subscription')
    )
    markup.row(types.InlineKeyboardButton('🔍 Check Subscription', callback_data='check_subscription'))
    markup.row(types.InlineKeyboardButton('🔙 Back to Main', callback_data='back_to_main'))
    return markup

def create_free_settings_panel():
    settings = get_free_user_settings()
    enabled = settings.get('enabled', 'True') == 'True'
    file_limit = settings.get('file_limit', '1')
    hosting_hours = settings.get('hosting_hours', '24')
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.row(
        types.InlineKeyboardButton(f"✅ Enabled" if enabled else "❌ Disabled", 
                                   callback_data=f'toggle_free_{not enabled}')
    )
    markup.row(
        types.InlineKeyboardButton(f"📁 File Limit: {file_limit}", callback_data='set_free_files'),
        types.InlineKeyboardButton(f"⏰ Hours: {hosting_hours}", callback_data='set_free_hours')
    )
    markup.row(types.InlineKeyboardButton("🔙 Back to Admin", callback_data='admin_panel'))
    return markup

# ============================================================
# SYSTEM STATS
# ============================================================

def get_system_stats():
    try:
        cpu_percent = psutil.cpu_percent(interval=0.5)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        stats = {
            'cpu': cpu_percent,
            'memory_total': memory.total / (1024**3),
            'memory_used': memory.used / (1024**3),
            'memory_percent': memory.percent,
            'disk_total': disk.total / (1024**3),
            'disk_used': disk.used / (1024**3),
            'disk_percent': disk.percent,
            'running_bots': len(bot_scripts),
            'total_users': len(active_users)
        }
        return stats
    except Exception as e:
        logger.error(f"Error getting system stats: {e}")
        return None

# ============================================================
# LOGIC FUNCTIONS
# ============================================================

def _logic_send_welcome(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    user_name = message.from_user.first_name
    user_username = message.from_user.username

    logger.info(f"Welcome request from user_id: {user_id}, username: @{user_username}")

    if bot_locked and user_id not in admin_ids:
        bot.send_message(chat_id, "🔒 Bot locked by admin. Try later.")
        return

    if user_id in user_ban:
        bot.send_message(chat_id, "🚫 You are banned from using this bot.")
        return

    user_bio = "Could not fetch bio"; photo_file_id = None
    try: user_bio = bot.get_chat(user_id).bio or "No bio"
    except Exception: pass
    try:
        user_profile_photos = bot.get_user_profile_photos(user_id, limit=1)
        if user_profile_photos.photos: photo_file_id = user_profile_photos.photos[0][-1].file_id
    except Exception: pass

    if user_id not in active_users:
        add_active_user(user_id)
        try:
            owner_notification = (f"🌟 New user!\nName: {user_name}\nUser: @{user_username or 'N/A'}\n"
                                  f"ID: `{user_id}`\nBio: {user_bio}")
            bot.send_message(OWNER_ID, owner_notification, parse_mode='Markdown')
            if photo_file_id: bot.send_photo(OWNER_ID, photo_file_id, caption=f"Pic of new user {user_id}")
        except Exception as e: logger.error(f"Failed to notify owner about new user {user_id}: {e}")

    file_limit = get_user_file_limit(user_id)
    current_files = get_user_file_count(user_id)
    limit_str = "Unlimited" if file_limit == float('inf') else str(file_limit)
    expiry_info = ""
    
    if user_id == OWNER_ID: 
        user_status = "👑 Owner"
    elif user_id in admin_ids: 
        user_status = "👨‍💼 Admin"
    elif user_id in user_vip:
        vip_time = user_vip[user_id].get('vip_time')
        if vip_time and vip_time > datetime.now():
            user_status = "⭐ VIP"
            days_left = (vip_time - datetime.now()).days
            expiry_info = f"\n⏰ VIP expires in: {days_left} days"
        else:
            user_status = "Free User"
    elif user_id in user_prime:
        prime_time = user_prime[user_id].get('prime_time')
        if prime_time and prime_time > datetime.now():
            user_status = "🔱 PRIME"
            days_left = (prime_time - datetime.now()).days
            expiry_info = f"\n⏰ Prime expires in: {days_left} days"
        else:
            user_status = "Free User"
    elif user_id in user_subscriptions:
        expiry_date = user_subscriptions[user_id].get('expiry')
        if expiry_date and expiry_date > datetime.now():
            user_status = "Premium"
            days_left = (expiry_date - datetime.now()).days
            expiry_info = f"\n⏰ Subscription expires in: {days_left} days"
        else:
            user_status = "Free User (Expired Sub)"
            remove_subscription_db(user_id)
    else:
        user_status = "Free User"

    if user_id in user_hosting:
        hosting_time = user_hosting[user_id].get('hosting_time')
        if hosting_time and hosting_time > datetime.now():
            remaining = hosting_time - datetime.now()
            hours_left = remaining.seconds // 3600
            minutes_left = (remaining.seconds % 3600) // 60
            expiry_info += f"\n⏰ Hosting left: {hours_left}h {minutes_left}m"
        else:
            del user_hosting[user_id]
            expiry_info += f"\n⏰ Hosting expired"

    welcome_msg_text = (f"🌟 **Welcome, {user_name}!** 🌟\n\n"
                        f"🆔 User ID: `{user_id}`\n"
                        f"👤 Username: `@{user_username or 'Not set'}`\n"
                        f"📊 Status: {user_status}{expiry_info}\n"
                        f"📁 Files: {current_files} / {limit_str}\n\n"
                        f"⚡ Host Python (`.py`) or JS (`.js`) scripts.\n"
                        f"📦 Upload single scripts or `.zip` archives.\n\n"
                        f"⚡ Response Time: 10ms (Flash of Light ⚡)\n"
                        f"💾 RAM: 500GB\n"
                        f"📁 Storage: Unlimited\n\n"
                        f"💡 Use buttons below or type commands!")
    
    main_reply_markup = create_reply_keyboard_ultra(user_id)
    try:
        if photo_file_id: bot.send_photo(chat_id, photo_file_id)
        bot.send_message(chat_id, welcome_msg_text, reply_markup=main_reply_markup, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Error sending welcome to {user_id}: {e}", exc_info=True)
        try: bot.send_message(chat_id, welcome_msg_text, reply_markup=main_reply_markup, parse_mode='Markdown')
        except Exception as fallback_e: logger.error(f"Fallback send_message failed for {user_id}: {fallback_e}")

def _logic_price_list(message):
    """Show Ultra Price List"""
    text = """╔══════════════════════════════════════╗
║       💲 PRICE LIST 💲               ║
╠══════════════════════════════════════╣
║                                      ║
║  🥇 PRIME PLANS                     ║
║  ───────────────────────             ║
║  🚀 5 Days      = ₹50              ║
║  💫 15 Days     = ₹100             ║
║  🔥 30 Days     = ₹199             ║
║  ⚡ 40 Days     = ₹240             ║
║  💎 60 Days     = ₹299             ║
║  👑 80 Days     = ₹499             ║
║  🌙 150 Days    = ₹799             ║
║  🌟 365 Days    = ₹999             ║
║                                      ║
║  ⭐ VIP PLANS                       ║
║  ───────────────────────             ║
║  💜 30 Days     = ₹300             ║
║  ✨ 60 Days     = ₹600             ║
║  ⭐ 80 Days     = ₹800             ║
║  🌌 150 Days    = ₹1500            ║
║  🏆 200 Days    = ₹2000            ║
║  👑 365 Days    = ₹36500           ║
║  ♾️ Life Time   = ₹10000           ║
║                                      ║
╠══════════════════════════════════════╣
║                                      ║
║  📞 Contact: {YOUR_USERNAME}         ║
║                                      ║
╚══════════════════════════════════════╝
    
💡 Click below for details or contact owner!"""
    
    markup = create_ultra_price_list()
    bot.reply_to(message, text, reply_markup=markup, parse_mode='Markdown')

def _logic_updates_channel(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('📢 Updates Channel', url=UPDATE_CHANNEL))
    bot.reply_to(message, "📢 Visit our Updates Channel:", reply_markup=markup)

def _logic_upload_file(message):
    user_id = message.from_user.id
    if bot_locked and user_id not in admin_ids:
        bot.reply_to(message, "🔒 Bot locked by admin, cannot accept files.")
        return

    if user_id in user_ban:
        bot.reply_to(message, "🚫 You are banned from using this bot.")
        return

    if not can_user_host(user_id):
        bot.reply_to(message, "⏰ Your hosting time has expired! Please contact admin to renew.\n\n"
                             f"📞 Contact: {YOUR_USERNAME}")
        return

    file_limit = get_user_file_limit(user_id)
    current_files = get_user_file_count(user_id)
    if current_files >= file_limit:
        limit_str = "Unlimited" if file_limit == float('inf') else str(file_limit)
        bot.reply_to(message, f"📁 File limit ({current_files}/{limit_str}) reached. Delete files first.")
        return
    bot.reply_to(message, "📤 Send your Python (`.py`), JS (`.js`), or ZIP (`.zip`) file.\n\n"
                         f"⏰ You have hosting time remaining!")

def _logic_check_files(message):
    user_id = message.from_user.id
    user_files_list = user_files.get(user_id, [])
    if not user_files_list:
        bot.reply_to(message, "📁 Your files:\n\n(No files uploaded yet)")
        return
    markup = types.InlineKeyboardMarkup(row_width=1)
    for file_name, file_type in sorted(user_files_list):
        is_running = is_bot_running(user_id, file_name)
        status_icon = "🟢 Running" if is_running else "🔴 Stopped"
        btn_text = f"{file_name} ({file_type}) - {status_icon}"
        markup.add(types.InlineKeyboardButton(btn_text, callback_data=f'file_{user_id}_{file_name}'))
    bot.reply_to(message, "📁 Your files:\nClick to manage.", reply_markup=markup, parse_mode='Markdown')

def _logic_bot_speed(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    start_time_ping = time.time()
    wait_msg = bot.reply_to(message, "⚡ Testing speed...")
    try:
        bot.send_chat_action(chat_id, 'typing')
        response_time = round((time.time() - start_time_ping) * 1000, 2)
        status = "🔓 Unlocked" if not bot_locked else "🔒 Locked"
        if user_id == OWNER_ID: user_level = "👑 Owner"
        elif user_id in admin_ids: user_level = "👨‍💼 Admin"
        elif user_id in user_vip:
            vip_time = user_vip[user_id].get('vip_time')
            if vip_time and vip_time > datetime.now():
                user_level = "⭐ VIP"
            else:
                user_level = "Free User"
        elif user_id in user_prime:
            prime_time = user_prime[user_id].get('prime_time')
            if prime_time and prime_time > datetime.now():
                user_level = "🔱 PRIME"
            else:
                user_level = "Free User"
        elif user_id in user_subscriptions and user_subscriptions[user_id].get('expiry', datetime.min) > datetime.now():
            user_level = "Premium"
        else:
            user_level = "Free User"
        speed_msg = (f"⚡ **Bot Speed & Status** ⚡\n\n"
                     f"📡 API Response Time: `{response_time} ms`\n"
                     f"🔓 Bot Status: {status}\n"
                     f"👤 Your Level: {user_level}\n\n"
                     f"⚡ Response Time: 10ms (Flash of Light)\n"
                     f"💾 RAM: 500GB\n"
                     f"📁 Storage: Unlimited")
        bot.edit_message_text(speed_msg, chat_id, wait_msg.message_id, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Error during speed test (cmd): {e}", exc_info=True)
        bot.edit_message_text("❌ Error during speed test.", chat_id, wait_msg.message_id)

def _logic_contact_owner(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('📞 Contact Owner', url=f'https://t.me/{YOUR_USERNAME.replace("@", "")}'))
    bot.reply_to(message, "📞 Click to contact Owner:", reply_markup=markup)

def _logic_uptime(message):
    uptime_str = get_uptime()
    bot.reply_to(message, f"⏱ Bot Uptime: `{uptime_str}`", parse_mode='Markdown')

def _logic_statistics(message):
    user_id = message.from_user.id
    total_users = len(active_users)
    total_files_records = sum(len(files) for files in user_files.values())

    running_bots_count = 0
    user_running_bots = 0

    for script_key_iter, script_info_iter in list(bot_scripts.items()):
        s_owner_id, _ = script_key_iter.split('_', 1)
        if is_bot_running(int(s_owner_id), script_info_iter['file_name']):
            running_bots_count += 1
            if int(s_owner_id) == user_id:
                user_running_bots +=1

    stats_msg_base = (f"📊 **Bot Statistics** 📊\n\n"
                      f"👥 Total Users: {total_users}\n"
                      f"📁 Total File Records: {total_files_records}\n"
                      f"🤖 Total Active Bots: {running_bots_count}\n")

    if user_id in admin_ids:
        vip_count = len(user_vip)
        prime_count = len(user_prime)
        banned_count = len(user_ban)
        stats_msg_admin = (f"\n👑 **Admin Stats:**\n"
                           f"⭐ VIP Users: {vip_count}\n"
                           f"🔱 Prime Users: {prime_count}\n"
                           f"🚫 Banned Users: {banned_count}\n"
                           f"🔒 Bot Status: {'Locked' if bot_locked else 'Unlocked'}\n"
                           f"🤖 Your Running Bots: {user_running_bots}")
        stats_msg = stats_msg_base + stats_msg_admin
    else:
        stats_msg = stats_msg_base + f"\n🤖 Your Running Bots: {user_running_bots}"

    bot.reply_to(message, stats_msg, parse_mode='Markdown')

def _logic_system_stats(message):
    if message.from_user.id not in admin_ids:
        bot.reply_to(message, "👑 Admin permissions required.")
        return
    
    stats = get_system_stats()
    if stats:
        text = f"""╔══════════════════════════════════════╗
║       📊 SYSTEM STATISTICS 📊        ║
╠══════════════════════════════════════╣
║                                      ║
║  💻 CPU: {stats['cpu']}%                     ║
║  🧠 Memory: {stats['memory_used']:.1f}GB / {stats['memory_total']:.1f}GB  ║
║  💾 Disk: {stats['disk_used']:.1f}GB / {stats['disk_total']:.1f}GB      ║
║                                      ║
║  🤖 Running Bots: {stats['running_bots']}         ║
║  👥 Total Users: {stats['total_users']}          ║
║                                      ║
║  ⚡ Response: 10ms (Flash of Light)  ║
║  💾 RAM: 500GB                       ║
║  📁 Storage: Unlimited               ║
║                                      ║
║  ⏱ Uptime: {get_uptime()}           ║
║                                      ║
╚══════════════════════════════════════╝"""
        bot.reply_to(message, text, parse_mode='Markdown')
    else:
        bot.reply_to(message, "❌ Failed to get system statistics.")

# ============================================================
# COMMAND HANDLERS
# ============================================================

@bot.message_handler(commands=['start', 'help'])
def command_send_welcome(message):
    _logic_send_welcome(message)

@bot.message_handler(commands=['price'])
def price_command(message):
    _logic_price_list(message)

@bot.message_handler(commands=['ping'])
def ping(message):
    start_ping_time = time.time()
    msg = bot.reply_to(message, "🏓 Pong!")
    latency = round((time.time() - start_ping_time) * 1000, 2)
    uptime_str = get_uptime()
    bot.edit_message_text(f"🏓 Pong!\n📡 Latency: {latency} ms\n⏱ Uptime: {uptime_str}\n⚡ Response Time: 10ms",
                          message.chat.id, msg.message_id)

@bot.message_handler(commands=['uptime'])
def command_uptime(message):
    _logic_uptime(message)

@bot.message_handler(commands=['chatgpt', 'gpt', 'ai'])
def handle_chatgpt(message):
    user_id = message.from_user.id
    if bot_locked and user_id not in admin_ids:
        bot.reply_to(message, "🔒 Bot is currently locked. Try again later.")
        return

    if user_id in user_ban:
        bot.reply_to(message, "🚫 You are banned from using this bot.")
        return

    if not message.text or len(message.text.split()) < 2:
        bot.reply_to(message, "🤖 Please provide a query after command.\nExample: `/chatgpt What is AI?`", parse_mode='Markdown')
        return

    query = message.text.split(' ', 1)[1]
    bot.send_chat_action(message.chat.id, 'typing')
    
    bot.send_message(message.chat.id, "🤖 Thinking...")
    
    try:
        response = chatgpt_query(query)
        
        if len(response) > 4000:
            for x in range(0, len(response), 4000):
                bot.reply_to(message, response[x:x+4000], parse_mode='Markdown')
        else:
            bot.reply_to(message, response, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"ChatGPT error: {e}")
        bot.reply_to(message, "❌ An error occurred while processing your request. Please try again later.")

@bot.message_handler(commands=['mpx'])
def handle_mpx_command(message):
    user_id = message.from_user.id
    if bot_locked and user_id not in admin_ids:
        bot.reply_to(message, "🔒 Bot is currently locked. Try again later.")
        return

    if user_id in user_ban:
        bot.reply_to(message, "🚫 You are banned from using this bot.")
        return

    if not message.text or len(message.text.split()) < 2:
        bot.reply_to(message, "🤖 Please provide a query after /mpx command.\nExample: `/mpx What is AI?`", parse_mode='Markdown')
        return

    query = message.text.split(' ', 1)[1]
    bot.send_chat_action(message.chat.id, 'typing')
    
    try:
        response = chatgpt_query(query)
        
        if len(response) > 4000:
            for x in range(0, len(response), 4000):
                bot.reply_to(message, response[x:x+4000], parse_mode='Markdown')
        else:
            bot.reply_to(message, response, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"MPX error: {e}")
        bot.reply_to(message, "❌ An error occurred while processing your request. Please try again later.")

# ============================================================
# BUTTON HANDLERS
# ============================================================

BUTTON_TEXT_TO_LOGIC = {
    "📢 Updates Channel": _logic_updates_channel,
    "📤 Upload File": _logic_upload_file,
    "📂 Check Files": _logic_check_files,
    "⚡ Bot Speed": _logic_bot_speed,
    "📞 Contact Owner": _logic_contact_owner,
    "📊 Statistics": _logic_statistics,
    "⏱ Uptime": _logic_uptime,
    "💲 Price List": _logic_price_list,
    "🤖 ChatGPT": handle_chatgpt,
    "🎮 Game Zone": lambda m: create_game_zone(m.chat.id),
}

@bot.message_handler(func=lambda message: message.text in BUTTON_TEXT_TO_LOGIC)
def handle_button_text(message):
    logic_func = BUTTON_TEXT_TO_LOGIC.get(message.text)
    if logic_func: 
        try:
            logic_func(message)
        except Exception as e:
            logger.error(f"Error in button handler {message.text}: {e}", exc_info=True)
            bot.reply_to(message, "❌ Error processing request. Try again.")
    else:
        logger.warning(f"Button text '{message.text}' matched but no logic func.")

# ============================================================
# CALLBACK HANDLERS
# ============================================================

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    user_id = call.from_user.id
    data = call.data
    logger.info(f"Callback: User={user_id}, Data='{data}'")

    # =============== PRICE LIST ===============
    if data == 'price_list':
        bot.answer_callback_query(call.id, "💲 Loading Price List...")
        _logic_price_list(call.message)
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except:
            pass
        return
    
    if data == 'show_prime_plans':
        bot.answer_callback_query(call.id, "🥇 Loading Prime Plans...")
        show_prime_plans_ultra(call.message.chat.id, call.message.message_id)
        return
    
    if data == 'show_vip_plans':
        bot.answer_callback_query(call.id, "⭐ Loading VIP Plans...")
        show_vip_plans_ultra(call.message.chat.id, call.message.message_id)
        return
    
    if data == 'back_to_prime_plans':
        bot.answer_callback_query(call.id, "🔙 Back to Prime Plans")
        show_prime_plans_ultra(call.message.chat.id, call.message.message_id)
        return
    
    if data == 'back_to_vip_plans':
        bot.answer_callback_query(call.id, "🔙 Back to VIP Plans")
        show_vip_plans_ultra(call.message.chat.id, call.message.message_id)
        return

    # =============== BUY PLAN ===============
    if data.startswith('buy_prime_'):
        try:
            parts = data.split('_')
            days = int(parts[2])
            plan_name = '_'.join(parts[3:])
            
            plan_data = PRIME_PLANS.get(plan_name)
            if not plan_data:
                for name, info in PRIME_PLANS.items():
                    if info['days'] == days:
                        plan_name = name
                        plan_data = info
                        break
            
            if plan_data:
                bot.answer_callback_query(call.id, f"📝 {plan_name} selected!")
                show_plan_details_ultra(
                    call.message.chat.id, 
                    call.message.message_id,
                    "PRIME",
                    plan_name,
                    days,
                    plan_data['price'],
                    plan_data['qr'],
                    plan_data['emoji']
                )
            else:
                bot.answer_callback_query(call.id, "❌ Plan not found!", show_alert=True)
            return
        except Exception as e:
            logger.error(f"Buy prime error: {e}")
            bot.answer_callback_query(call.id, "❌ Error!", show_alert=True)
            return
    
    if data.startswith('buy_vip_'):
        try:
            parts = data.split('_')
            days = int(parts[2])
            plan_name = '_'.join(parts[3:])
            
            plan_data = VIP_PLANS.get(plan_name)
            if not plan_data:
                for name, info in VIP_PLANS.items():
                    if info['days'] == days:
                        plan_name = name
                        plan_data = info
                        break
            
            if plan_data:
                bot.answer_callback_query(call.id, f"📝 {plan_name} selected!")
                show_plan_details_ultra(
                    call.message.chat.id, 
                    call.message.message_id,
                    "VIP",
                    plan_name,
                    days,
                    plan_data['price'],
                    plan_data['qr'],
                    plan_data['emoji']
                )
            else:
                bot.answer_callback_query(call.id, "❌ Plan not found!", show_alert=True)
            return
        except Exception as e:
            logger.error(f"Buy vip error: {e}")
            bot.answer_callback_query(call.id, "❌ Error!", show_alert=True)
            return

    # =============== PAYMENT ===============
    if data.startswith('pay_done_'):
        try:
            parts = data.split('_')
            plan_type = parts[2]
            days = int(parts[3])
            
            if plan_type == "prime":
                plan_name = [k for k, v in PRIME_PLANS.items() if v['days'] == days][0]
                price = PRIME_PLANS[plan_name]['price']
                plan_type_display = "🥇 PRIME"
            else:
                plan_name = [k for k, v in VIP_PLANS.items() if v['days'] == days][0]
                price = VIP_PLANS[plan_name]['price']
                plan_type_display = "⭐ VIP"
            
            bot.answer_callback_query(call.id, "✅ Payment notification sent to owner!")
            
            send_payment_notification(user_id, plan_type_display, plan_name, days, price)
            
            bot.send_message(call.message.chat.id, 
                            f"✅ **Payment Confirmed!**\n\n"
                            f"📝 Plan: {plan_name}\n"
                            f"💰 Price: {price}\n"
                            f"📅 Duration: {days} days\n\n"
                            f"⏳ Please wait for admin to activate your subscription.\n\n"
                            f"📞 Contact: {YOUR_USERNAME}", parse_mode='Markdown')
            
            try:
                bot.delete_message(call.message.chat.id, call.message.message_id)
            except:
                pass
            return
        except Exception as e:
            logger.error(f"Pay done error: {e}")
            bot.answer_callback_query(call.id, "❌ Error!", show_alert=True)
            return
    
    if data == 'pay_reject':
        bot.answer_callback_query(call.id, "❌ Payment rejected!")
        bot.send_message(call.message.chat.id, 
                        f"❌ **Payment Rejected!**\n\n"
                        f"If you have any questions, contact: {YOUR_USERNAME}", parse_mode='Markdown')
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except:
            pass
        return

    # =============== GAME ZONE ===============
    if data == 'games':
        bot.answer_callback_query(call.id, "🎮 Loading Games...")
        create_game_zone(call.message.chat.id)
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except:
            pass
        return
    
    if data == 'spin_wheel':
        bot.answer_callback_query(call.id, "🎰 Spinning...")
        spin_wheel(call.message.chat.id)
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except:
            pass
        return
    
    if data == 'roll_dice':
        bot.answer_callback_query(call.id, "🎲 Rolling...")
        roll_dice(call.message.chat.id)
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except:
            pass
        return
    
    if data == 'card_game':
        bot.answer_callback_query(call.id, "🃏 Dealing...")
        card_game(call.message.chat.id)
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except:
            pass
        return
    
    if data == 'fortune_teller':
        bot.answer_callback_query(call.id, "🔮 Reading fortunes...")
        fortune_teller(call.message.chat.id)
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except:
            pass
        return
    
    if data == 'speed_test':
        bot.answer_callback_query(call.id, "⚡ Get ready!")
        speed_test(call.message.chat.id)
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except:
            pass
        return
    
    if data == 'guess_number':
        bot.answer_callback_query(call.id, "🎯 Starting game...")
        guess_number(call.message.chat.id)
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except:
            pass
        return
    
    if data.startswith('guess_'):
        guess = int(data.split('_')[1])
        handle_guess(call.message.chat.id, user_id, guess)
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except:
            pass
        return

    # =============== ADMIN CALLBACKS ===============
    if data == 'admin_panel':
        if user_id not in admin_ids:
            bot.answer_callback_query(call.id, "👑 Admin only!", show_alert=True)
            return
        bot.answer_callback_query(call.id, "👑 Admin Panel")
        try:
            bot.edit_message_text("👑 **Admin Panel**\nManage admins & settings.",
                                  call.message.chat.id, call.message.message_id, 
                                  reply_markup=create_admin_panel(), parse_mode='Markdown')
        except:
            bot.send_message(call.message.chat.id, "👑 **Admin Panel**", 
                            reply_markup=create_admin_panel(), parse_mode='Markdown')
        return

    # =============== BACK TO MAIN ===============
    if data == 'back_to_main':
        bot.answer_callback_query(call.id, "🔙 Back to Main")
        try:
            _logic_send_welcome(call.message)
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except:
            pass
        return

    # =============== OTHER CALLBACKS ===============
    if data == 'chatgpt':
        bot.answer_callback_query(call.id, "🤖 ChatGPT")
        bot.send_message(call.message.chat.id, 
                        "🤖 **ChatGPT**\n\n"
                        "Send your query using:\n"
                        "`/chatgpt Your question`\n"
                        "`/gpt Your question`\n"
                        "`/ai Your question`\n\n"
                        "Or simply type `/mpx Your question`", parse_mode='Markdown')
        return
    
    if data == 'uptime':
        bot.answer_callback_query(call.id, "⏱ Checking uptime...")
        uptime_str = get_uptime()
        bot.send_message(call.message.chat.id, f"⏱ Bot Uptime: `{uptime_str}`", parse_mode='Markdown')
        return

    # ... More callback handlers ...

# ============================================================
# SCHEDULER
# ============================================================

def check_expired_hosting():
    current_time = datetime.now()
    for user_id, hosting_data in list(user_hosting.items()):
        if hosting_data['hosting_time'] <= current_time:
            for file_name, _ in user_files.get(user_id, []):
                script_key = f"{user_id}_{file_name}"
                if script_key in bot_scripts:
                    kill_process_tree(bot_scripts[script_key])
                    del bot_scripts[script_key]
            del user_hosting[user_id]
            with DB_LOCK:
                conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
                c = conn.cursor()
                c.execute('DELETE FROM user_hosting WHERE user_id = ?', (user_id,))
                conn.commit()
                conn.close()
            try:
                bot.send_message(user_id, "⏰ Your hosting time has expired! Your bots have been stopped.\n\n"
                                         f"📞 Contact: {YOUR_USERNAME}")
            except Exception as e:
                logger.error(f"Failed to notify {user_id} about expired hosting: {e}")

def check_expired_prime():
    current_time = datetime.now()
    for user_id, prime_data in list(user_prime.items()):
        if prime_data['prime_time'] <= current_time:
            del user_prime[user_id]
            with DB_LOCK:
                conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
                c = conn.cursor()
                c.execute('DELETE FROM user_prime WHERE user_id = ?', (user_id,))
                conn.commit()
                conn.close()
            try:
                bot.send_message(user_id, "⏰ Your prime status has expired!")
            except Exception as e:
                logger.error(f"Failed to notify {user_id} about expired prime: {e}")

def check_expired_vip():
    current_time = datetime.now()
    for user_id, vip_data in list(user_vip.items()):
        if vip_data['vip_time'] <= current_time:
            del user_vip[user_id]
            with DB_LOCK:
                conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
                c = conn.cursor()
                c.execute('DELETE FROM user_vip WHERE user_id = ?', (user_id,))
                conn.commit()
                conn.close()
            try:
                bot.send_message(user_id, "⏰ Your VIP status has expired!")
            except Exception as e:
                logger.error(f"Failed to notify {user_id} about expired vip: {e}")

def schedule_check():
    while True:
        check_expired_hosting()
        check_expired_prime()
        check_expired_vip()
        time.sleep(60)

# ============================================================
# CLEANUP
# ============================================================

def cleanup():
    logger.warning("Shutdown. Cleaning up processes...")
    script_keys_to_stop = list(bot_scripts.keys())
    if not script_keys_to_stop: logger.info("No scripts running. Exiting."); return
    logger.info(f"Stopping {len(script_keys_to_stop)} scripts...")
    for key in script_keys_to_stop:
        if key in bot_scripts: logger.info(f"Stopping: {key}"); kill_process_tree(bot_scripts[key])
        else: logger.info(f"Script {key} already removed.")
    logger.warning("Cleanup finished.")

atexit.register(cleanup)

# ============================================================
# MAIN
# ============================================================

if __name__ == '__main__':
    print("="*60)
    print("🌟 BRONX ULTRA OSINT BOT V100 ULTRA ADVANCED 🌟")
    print(f"🐍 Python: {sys.version.split()[0]}")
    print(f"📁 Base Dir: {BASE_DIR}")
    print(f"👑 Owner ID: {OWNER_ID}")
    print(f"⚡ Response Time: 10ms (Flash of Light)")
    print(f"💾 RAM: 500GB")
    print(f"📁 Storage: Unlimited")
    print("="*60)
    
    keep_alive()
    scheduler_thread = threading.Thread(target=schedule_check, daemon=True)
    scheduler_thread.start()
    logger.info("🚀 Starting polling...")
    
    while True:
        try:
            bot.infinity_polling(logger_level=logging.INFO, timeout=60, long_polling_timeout=30)
        except requests.exceptions.ReadTimeout:
            logger.warning("⏱ Polling ReadTimeout. Restarting in 5s...")
            time.sleep(5)
        except requests.exceptions.ConnectionError as ce:
            logger.error(f"🔌 Polling ConnectionError: {ce}. Retrying in 15s...")
            time.sleep(15)
        except Exception as e:
            logger.critical(f"💥 Unrecoverable polling error: {e}", exc_info=True)
            logger.info("🔄 Restarting polling in 30s due to critical error...")
            time.sleep(30)
        finally:
            logger.warning("🔄 Polling attempt finished. Will restart if in loop.")
            time.sleep(1)

# ============================================================
# END OF CODE
# ============================================================
