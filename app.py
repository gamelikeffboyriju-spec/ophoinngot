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

from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "🤖 BRONX ULTRA OSINT BOT v21.0 is running!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()
    print("🚀 Flask Keep-Alive server started.")

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

# =============== FREE CHATGPT API ===============
CHATGPT_API_URL = "https://api.itsrose.life/ai/chatgpt"
CHATGPT_API_KEY = "rose"

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_BOTS_DIR = os.path.join(BASE_DIR, 'upload_bots')
IROTECH_DIR = os.path.join(BASE_DIR, 'inf')
DATABASE_PATH = os.path.join(IROTECH_DIR, 'bot_data.db')

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

# =============== SUBSCRIPTION PLANS WITH QR ===============
PRIME_PLANS = {
    "5 Days": {"days": 5, "price": "₹50", "qr": "https://i.ibb.co/mVyp4G45/Screenshot-20260730-144036-1.jpg"},
    "15 Days": {"days": 15, "price": "₹100", "qr": "https://i.ibb.co/mVyp4G45/Screenshot-20260730-144036-1.jpg"},
    "30 Days": {"days": 30, "price": "₹199", "qr": "https://i.ibb.co/mVyp4G45/Screenshot-20260730-144036-1.jpg"},
    "40 Days": {"days": 40, "price": "₹240", "qr": "https://i.ibb.co/mVyp4G45/Screenshot-20260730-144036-1.jpg"},
    "60 Days": {"days": 60, "price": "₹299", "qr": "https://i.ibb.co/mVyp4G45/Screenshot-20260730-144036-1.jpg"},
    "80 Days": {"days": 80, "price": "₹499", "qr": "https://i.ibb.co/mVyp4G45/Screenshot-20260730-144036-1.jpg"},
    "150 Days": {"days": 150, "price": "₹799", "qr": "https://i.ibb.co/mVyp4G45/Screenshot-20260730-144036-1.jpg"},
    "365 Days": {"days": 365, "price": "₹999", "qr": "https://i.ibb.co/mVyp4G45/Screenshot-20260730-144036-1.jpg"}
}

VIP_PLANS = {
    "30 Days": {"days": 30, "price": "₹300", "qr": "https://i.ibb.co/mVyp4G45/Screenshot-20260730-144036-1.jpg"},
    "60 Days": {"days": 60, "price": "₹600", "qr": "https://i.ibb.co/mVyp4G45/Screenshot-20260730-144036-1.jpg"},
    "80 Days": {"days": 80, "price": "₹800", "qr": "https://i.ibb.co/mVyp4G45/Screenshot-20260730-144036-1.jpg"},
    "150 Days": {"days": 150, "price": "₹1500", "qr": "https://i.ibb.co/mVyp4G45/Screenshot-20260730-144036-1.jpg"},
    "200 Days": {"days": 200, "price": "₹2000", "qr": "https://i.ibb.co/mVyp4G45/Screenshot-20260730-144036-1.jpg"},
    "365 Days": {"days": 365, "price": "₹36500", "qr": "https://i.ibb.co/mVyp4G45/Screenshot-20260730-144036-1.jpg"},
    "Life Time": {"days": 99999, "price": "₹10000", "qr": "https://i.ibb.co/mVyp4G45/Screenshot-20260730-144036-1.jpg"}
}

COMMAND_BUTTONS_LAYOUT_USER_SPEC = [
    ["📢 Updates Channel", "⏱ Uptime"],
    ["📤 Upload File", "📂 Check Files"],
    ["⚡ Bot Speed", "📊 Statistics"],
    ["💲 Price List", "📞 Contact Owner"],
    ["🤖 ChatGPT"]
]

ADMIN_COMMAND_BUTTONS_LAYOUT_USER_SPEC = [
    ["📢 Updates Channel", "/ping"],
    ["📤 Upload File", "📂 Check Files"],
    ["⚡ Bot Speed", "📊 Statistics"],
    ["💳 Subscriptions", "📢 Broadcast"],
    ["🔒 Lock Bot", "🟢 Running All Code"],
    ["👑 Admin Panel", "📞 Contact Owner"],
    ["🤖 ChatGPT", "⏱ Uptime"],
    ["📂 Global History", "💲 Price List"],
    ["🖥️ Bot Manager", "📊 System Stats"]
]

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

# =============== RUN SCRIPT FUNCTIONS ===============

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

def run_js_script(script_path, script_owner_id, user_folder, file_name, message_obj_for_reply, attempt=1):
    max_attempts = 2
    if attempt > max_attempts:
        bot.reply_to(message_obj_for_reply, f"❌ Failed to run '{file_name}' after {max_attempts} attempts. Check logs.")
        return

    script_key = f"{script_owner_id}_{file_name}"
    logger.info(f"Attempt {attempt} to run JS script: {script_path} (Key: {script_key}) for user {script_owner_id}")

    if not can_user_host(script_owner_id):
        bot.reply_to(message_obj_for_reply, "⏰ Your hosting time has expired! Please contact admin.")
        return

    try:
        if not os.path.exists(script_path):
             bot.reply_to(message_obj_for_reply, f"❌ Script '{file_name}' not found!")
             logger.error(f"JS Script not found: {script_path} for user {script_owner_id}")
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
            logger.error(f"Failed to open log file '{log_file_path}' for JS script {script_key}: {e}", exc_info=True)
            bot.reply_to(message_obj_for_reply, f"❌ Failed to open log file '{log_file_path}': {e}")
            return

        env = os.environ.copy()
        env['NODE_PATH'] = user_folder + os.pathsep + env.get('NODE_PATH', '')

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
                ['node', script_path],
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
                logger.info(f"✅ Started JS process {process.pid} for {script_key}")
                
                bot_scripts[script_key] = {
                    'process': process,
                    'log_file': log_file,
                    'file_name': file_name,
                    'chat_id': message_obj_for_reply.chat.id,
                    'script_owner_id': script_owner_id,
                    'start_time': datetime.now(),
                    'user_folder': user_folder,
                    'type': 'js',
                    'script_key': script_key,
                    'log_path': log_file_path
                }
                
                bot.reply_to(message_obj_for_reply, 
                            f"✅ **JS Script Started Successfully!**\n\n"
                            f"📁 File: `{file_name}`\n"
                            f"🆔 PID: `{process.pid}`\n"
                            f"👤 User: `{script_owner_id}`\n\n"
                            f"⚡ Response Time: 10ms\n"
                            f"📜 Check logs using control buttons!")
                
                threading.Thread(target=monitor_bot_live, args=(script_key, process, log_file_path, file_name, script_owner_id), daemon=True).start()
                
            else:
                error_code = process.poll()
                log_content = get_last_log_lines(log_file_path, 20)
                
                error_hint = ""
                if "Cannot find module" in log_content:
                    error_hint = "\n🔧 **Missing Node Module!** Run `npm install` first."
                elif "SyntaxError" in log_content:
                    error_hint = "\n🔧 **Syntax Error!** Check your code."
                
                bot.reply_to(message_obj_for_reply, 
                            f"❌ **JS Script Crashed!**\n\n"
                            f"📁 File: `{file_name}`\n"
                            f"💀 Return Code: {error_code}\n\n"
                            f"📜 **Last Logs:**\n```\n{log_content[:1500]}\n```\n{error_hint}")
                
                if log_file and not log_file.closed:
                    log_file.close()
                if script_key in bot_scripts:
                    del bot_scripts[script_key]
                return

        except FileNotFoundError:
            error_msg = "❌ 'node' not found. Ensure Node.js is installed."
            logger.error(error_msg)
            bot.reply_to(message_obj_for_reply, error_msg)
            if log_file and not log_file.closed:
                log_file.close()
            if script_key in bot_scripts:
                del bot_scripts[script_key]
        except Exception as e:
            if log_file and not log_file.closed:
                log_file.close()
            error_msg = f"❌ Error starting JS script '{file_name}': {str(e)}"
            logger.error(error_msg, exc_info=True)
            bot.reply_to(message_obj_for_reply, error_msg)
            
            if process and process.poll() is None:
                logger.warning(f"Killing potentially started JS process {process.pid} for {script_key}")
                kill_process_tree({'process': process, 'log_file': log_file, 'script_key': script_key})
            if script_key in bot_scripts:
                del bot_scripts[script_key]

    except Exception as e:
        error_msg = f"❌ Unexpected error running JS script '{file_name}': {str(e)}"
        logger.error(error_msg, exc_info=True)
        bot.reply_to(message_obj_for_reply, error_msg)
        
        if script_key in bot_scripts:
            logger.warning(f"Cleaning up {script_key} due to error in run_js_script.")
            kill_process_tree(bot_scripts[script_key])
            del bot_scripts[script_key]

# =============== DATABASE FUNCTIONS ===============

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

# =============== UI FUNCTIONS ===============

def create_main_menu_inline(user_id):
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = [
        types.InlineKeyboardButton('📢 Updates Channel', url=UPDATE_CHANNEL),
        types.InlineKeyboardButton('📤 Upload File', callback_data='upload'),
        types.InlineKeyboardButton('📂 Check Files', callback_data='check_files'),
        types.InlineKeyboardButton('⚡ Bot Speed', callback_data='speed'),
        types.InlineKeyboardButton('📊 Statistics', callback_data='stats'),
        types.InlineKeyboardButton('💲 Price List', callback_data='price_list'),
        types.InlineKeyboardButton('📞 Contact Owner', url=f'https://t.me/{YOUR_USERNAME.replace("@", "")}'),
        types.InlineKeyboardButton('🤖 ChatGPT', callback_data='chatgpt')
    ]

    if user_id in admin_ids:
        admin_buttons = [
            types.InlineKeyboardButton('💳 Subscriptions', callback_data='subscription'),
            types.InlineKeyboardButton('📢 Broadcast', callback_data='broadcast'),
            types.InlineKeyboardButton('🔒 Lock Bot' if not bot_locked else '🔓 Unlock Bot',
                                     callback_data='lock_bot' if not bot_locked else 'unlock_bot'),
            types.InlineKeyboardButton('👑 Admin Panel', callback_data='admin_panel'),
            types.InlineKeyboardButton('🟢 Run All Scripts', callback_data='run_all_scripts'),
            types.InlineKeyboardButton('📂 Global History', callback_data='global_history'),
            types.InlineKeyboardButton('⚙️ Free Settings', callback_data='free_settings'),
            types.InlineKeyboardButton('🖥️ Bot Manager', callback_data='bot_manager'),
            types.InlineKeyboardButton('📊 System Stats', callback_data='system_stats')
        ]
        markup.add(buttons[0])
        markup.add(buttons[1], buttons[2])
        markup.add(buttons[3], admin_buttons[0])
        markup.add(buttons[4], admin_buttons[1])
        markup.add(admin_buttons[2], admin_buttons[4])
        markup.add(admin_buttons[3])
        markup.add(admin_buttons[5], admin_buttons[6])
        markup.add(admin_buttons[7], admin_buttons[8])
        markup.add(buttons[5], buttons[6])
        markup.add(buttons[7])
    else:
        markup.add(buttons[0])
        markup.add(buttons[1], buttons[2])
        markup.add(buttons[3])
        markup.add(buttons[4])
        markup.add(buttons[5])
        markup.add(buttons[6], buttons[7])

    markup.add(types.InlineKeyboardButton('⏱ Uptime', callback_data='uptime'))
    return markup

def create_reply_keyboard_main_menu(user_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    layout_to_use = ADMIN_COMMAND_BUTTONS_LAYOUT_USER_SPEC if user_id in admin_ids else COMMAND_BUTTONS_LAYOUT_USER_SPEC
    for row_buttons_text in layout_to_use:
        markup.add(*[types.KeyboardButton(text) for text in row_buttons_text])
    return markup

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

def create_admin_panel():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.row(
        types.InlineKeyboardButton('➕ Add Admin', callback_data='add_admin'),
        types.InlineKeyboardButton('➖ Remove Admin', callback_data='remove_admin')
    )
    markup.row(types.InlineKeyboardButton('📋 List Admins', callback_data='list_admins'))
    markup.row(types.InlineKeyboardButton('⚙️ Free Settings', callback_data='free_settings'))
    markup.row(types.InlineKeyboardButton('📂 Global History', callback_data='global_history'))
    markup.row(types.InlineKeyboardButton('💲 Price List', callback_data='price_list'))
    markup.row(types.InlineKeyboardButton('🖥️ Bot Manager', callback_data='bot_manager'))
    markup.row(types.InlineKeyboardButton('📊 System Stats', callback_data='system_stats'))
    markup.row(types.InlineKeyboardButton('👥 All Users Bots', callback_data='all_users_bots'))  # NEW
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

def create_price_list():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🥇 PRIME PLANS", callback_data='show_prime_plans'),
        types.InlineKeyboardButton("⭐ VIP PLANS", callback_data='show_vip_plans')
    )
    markup.add(
        types.InlineKeyboardButton("📞 Contact Owner", url=f'https://t.me/{YOUR_USERNAME.replace("@", "")}'),
        types.InlineKeyboardButton("🔙 Back to Main", callback_data='back_to_main')
    )
    return markup

def create_prime_plans():
    markup = types.InlineKeyboardMarkup(row_width=2)
    for plan_name, plan_data in PRIME_PLANS.items():
        markup.add(types.InlineKeyboardButton(
            f"{plan_name} - {plan_data['price']}", 
            callback_data=f'buy_prime_{plan_data["days"]}_{plan_name}'
        ))
    markup.add(types.InlineKeyboardButton("🔙 Back to Price List", callback_data='price_list'))
    return markup

def create_vip_plans():
    markup = types.InlineKeyboardMarkup(row_width=2)
    for plan_name, plan_data in VIP_PLANS.items():
        markup.add(types.InlineKeyboardButton(
            f"{plan_name} - {plan_data['price']}", 
            callback_data=f'buy_vip_{plan_data["days"]}_{plan_name}'
        ))
    markup.add(types.InlineKeyboardButton("🔙 Back to Price List", callback_data='price_list'))
    return markup

def create_payment_buttons(plan_type, plan_name, days, price):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton("✅ Payment Done", callback_data=f'pay_done_{plan_type}_{days}'))
    markup.add(types.InlineKeyboardButton("❌ Payment Reject", callback_data='pay_reject'))
    markup.add(types.InlineKeyboardButton("🔙 Back to Plans", callback_data=f'{plan_type}_plans'))
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

def handle_js_file(file_path, script_owner_id, user_folder, file_name, message):
    try:
        save_user_file(script_owner_id, file_name, 'js')
        threading.Thread(target=run_js_script, args=(file_path, script_owner_id, user_folder, file_name, message)).start()
    except Exception as e:
        logger.error(f"Error processing JS file {file_name} for {script_owner_id}: {e}", exc_info=True)
        bot.reply_to(message, f"❌ Error processing JS file: {str(e)}")

def handle_py_file(file_path, script_owner_id, user_folder, file_name, message):
    try:
        save_user_file(script_owner_id, file_name, 'py')
        threading.Thread(target=run_script, args=(file_path, script_owner_id, user_folder, file_name, message)).start()
    except Exception as e:
        logger.error(f"Error processing Python file {file_name} for {script_owner_id}: {e}", exc_info=True)
        bot.reply_to(message, f"❌ Error processing Python file: {str(e)}")

# =============== CHATGPT FUNCTIONS ===============

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
            # Fallback to another free API
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

# =============== PRICE LIST FUNCTIONS ===============

def show_price_list(chat_id, message_id=None):
    text = """💲 **Bot Hosting Subscription Plans** 💲

🌟 **Choose Your Perfect Plan:**

━━━━━━━━━━━━━━━━━━━━━━━━━
🥇 **PRIME PLANS** 🥇
━━━━━━━━━━━━━━━━━━━━━━━━━

✅ 5 Days = ₹50
✅ 15 Days = ₹100
✅ 30 Days = ₹199
✅ 40 Days = ₹240
✅ 60 Days = ₹299
✅ 80 Days = ₹499
✅ 150 Days = ₹799
✅ 365 Days = ₹999

🎁 **Prime Features:**
• 24/7 Working ✅
• All Time Running ✅
• No Stop ✅
• Fast Response ✅
• File Hosting Limit ✅
• Py, JS, ZIP Support ✅

━━━━━━━━━━━━━━━━━━━━━━━━━
⭐ **VIP PLANS** ⭐
━━━━━━━━━━━━━━━━━━━━━━━━━

✅ 30 Days = ₹300
✅ 60 Days = ₹600
✅ 80 Days = ₹800
✅ 150 Days = ₹1500
✅ 200 Days = ₹2000
✅ 365 Days = ₹36500
✅ Life Time = ₹10000

🎁 **VIP Features:**
• Unlimited File Hosting ✅
• No Limits ✅
• 24/7 Working ✅
• Ultra Fast Response ✅
• All Features Unlimited ✅
• Any File Support ✅

━━━━━━━━━━━━━━━━━━━━━━━━━
📞 **Contact Owner:** @BRONX_ULTRA
━━━━━━━━━━━━━━━━━━━━━━━━━

💡 Click below to buy or contact owner!"""

    markup = create_price_list()
    
    if message_id:
        try:
            bot.edit_message_text(text, chat_id, message_id, reply_markup=markup, parse_mode='Markdown')
        except Exception as e:
            logger.error(f"Error editing price list: {e}")
            bot.send_message(chat_id, text, reply_markup=markup, parse_mode='Markdown')
    else:
        bot.send_message(chat_id, text, reply_markup=markup, parse_mode='Markdown')

def show_prime_plans(chat_id, message_id):
    text = """🥇 **Prime Plans** 🥇

━━━━━━━━━━━━━━━━━━━━━━━━━
✅ 5 Days = ₹50
✅ 15 Days = ₹100
✅ 30 Days = ₹199
✅ 40 Days = ₹240
✅ 60 Days = ₹299
✅ 80 Days = ₹499
✅ 150 Days = ₹799
✅ 365 Days = ₹999
━━━━━━━━━━━━━━━━━━━━━━━━━

🎁 **Prime Features:**
• 24/7 Working ✅
• All Time Running ✅
• No Stop ✅
• Fast Response ✅
• File Hosting Limit ✅
• Py, JS, ZIP Support ✅

**Select a plan below:**"""
    
    try:
        bot.edit_message_text(text, chat_id, message_id, reply_markup=create_prime_plans(), parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Error showing prime plans: {e}")
        bot.send_message(chat_id, text, reply_markup=create_prime_plans(), parse_mode='Markdown')

def show_vip_plans(chat_id, message_id):
    text = """⭐ **VIP Plans** ⭐

━━━━━━━━━━━━━━━━━━━━━━━━━
✅ 30 Days = ₹300
✅ 60 Days = ₹600
✅ 80 Days = ₹800
✅ 150 Days = ₹1500
✅ 200 Days = ₹2000
✅ 365 Days = ₹36500
✅ Life Time = ₹10000
━━━━━━━━━━━━━━━━━━━━━━━━━

🎁 **VIP Features:**
• Unlimited File Hosting ✅
• No Limits ✅
• 24/7 Working ✅
• Ultra Fast Response ✅
• All Features Unlimited ✅
• Any File Support ✅

**Select a plan below:**"""
    
    try:
        bot.edit_message_text(text, chat_id, message_id, reply_markup=create_vip_plans(), parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Error showing vip plans: {e}")
        bot.send_message(chat_id, text, reply_markup=create_vip_plans(), parse_mode='Markdown')

def show_plan_details(chat_id, message_id, plan_type, plan_name, days, price, qr_url):
    text = f"""📝 **{plan_type} Plan Selected:** {plan_name}

💰 **Price:** {price}
📅 **Duration:** {days} days

🎁 **Features:**
"""
    if plan_type == "🥇 PRIME":
        text += """✅ 24/7 Working
✅ All Time Running
✅ No Stop
✅ Fast Response
✅ File Hosting Limit
✅ Py, JS, ZIP Support
"""
    else:
        text += """✅ Unlimited File Hosting
✅ No Limits
✅ 24/7 Working
✅ Ultra Fast Response
✅ All Features Unlimited
✅ Any File Support
"""
    
    text += f"""

📱 **Scan QR to Pay:**

📞 Contact: {YOUR_USERNAME}

⚠️ After payment, click **"Payment Done"** below!"""

    markup = create_payment_buttons("prime" if plan_type == "🥇 PRIME" else "vip", plan_name, days, price)
    
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

def save_pending_payment(user_id, plan_type, plan_name, days, price):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            c.execute('INSERT OR REPLACE INTO pending_payments (user_id, plan_type, plan_name, days, price, timestamp) VALUES (?, ?, ?, ?, ?, ?)',
                      (user_id, plan_type, plan_name, days, price, datetime.now().isoformat()))
            conn.commit()
            logger.info(f"Saved pending payment for user {user_id}: {plan_type} - {plan_name}")
        except Exception as e:
            logger.error(f"Error saving pending payment: {e}")
        finally:
            conn.close()

def get_user_info(user_id):
    try:
        user = bot.get_chat(user_id)
        name = user.first_name or "Unknown"
        username = user.username or "N/A"
        return name, username
    except:
        return "Unknown", "N/A"

def send_payment_notification(user_id, plan_type, plan_name, days, price):
    name, username = get_user_info(user_id)
    
    status = "Free User"
    if user_id in user_vip:
        vip_time = user_vip[user_id].get('vip_time')
        if vip_time and vip_time > datetime.now():
            status = "⭐ VIP"
    elif user_id in user_prime:
        prime_time = user_prime[user_id].get('prime_time')
        if prime_time and prime_time > datetime.now():
            status = "🔱 PRIME"
    elif user_id in admin_ids:
        status = "👑 Admin"
    elif user_id == OWNER_ID:
        status = "👑 Owner"
    
    # QR Code for payment
    qr_url = "https://i.ibb.co/mVyp4G45/Screenshot-20260730-144036-1.jpg"
    
    text = f"""💳 **Payment Notification** 💳

👤 **User Details:**
• Name: {name}
• Username: @{username}
• ID: `{user_id}`
• Current Status: {status}

📝 **Plan Selected:**
• Type: {plan_type}
• Plan: {plan_name}
• Duration: {days} days
• Price: {price}

📱 **QR Code for Payment:**
"""
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("✅ Approve & Add Prime", callback_data=f'add_prime_{user_id}_{days}'),
        types.InlineKeyboardButton("✅ Approve & Add VIP", callback_data=f'add_vip_{user_id}_{days}'),
        types.InlineKeyboardButton("❌ Reject Payment", callback_data=f'reject_payment_{user_id}')
    )
    
    try:
        # Send QR with payment instructions
        bot.send_photo(OWNER_ID, qr_url, caption=text, reply_markup=markup, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Error sending payment notification to owner: {e}")
        # Fallback: send without photo
        text += f"\n🔗 QR Link: {qr_url}"
        bot.send_message(OWNER_ID, text, reply_markup=markup, parse_mode='Markdown')

def send_subscription_confirmation(user_id, status_type, expiry_date):
    try:
        user = bot.get_chat(user_id)
        name = user.first_name or "Unknown"
        username = user.username or "N/A"
        
        text = f"""🎉 **Subscription Added Successfully!** 🎉

👤 **Your Details:**
• Name: {name}
• Username: @{username}
• ID: `{user_id}`
• Status: {status_type}
• Expiry Date: {expiry_date.strftime('%Y-%m-%d %H:%M:%S')}

✅ You now have access to all {status_type} features!

Any problem? Contact: {YOUR_USERNAME}"""
        
        bot.send_message(user_id, text, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Error sending subscription confirmation to user {user_id}: {e}")

def add_prime_to_user(user_id, days):
    expiry = datetime.now() + timedelta(days=days)
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            c.execute('INSERT OR REPLACE INTO user_prime (user_id, prime_time) VALUES (?, ?)',
                      (user_id, expiry.isoformat()))
            conn.commit()
            user_prime[user_id] = {'prime_time': expiry}
            logger.info(f"Added prime for user {user_id} for {days} days")
        except Exception as e:
            logger.error(f"Error adding prime: {e}")
        finally:
            conn.close()
    
    send_subscription_confirmation(user_id, "🔱 PRIME", expiry)
    
    try:
        bot.send_message(OWNER_ID, f"✅ Prime added to user {user_id} for {days} days!")
    except:
        pass

def add_vip_to_user(user_id, days):
    expiry = datetime.now() + timedelta(days=days)
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            c.execute('INSERT OR REPLACE INTO user_vip (user_id, vip_time) VALUES (?, ?)',
                      (user_id, expiry.isoformat()))
            conn.commit()
            user_vip[user_id] = {'vip_time': expiry}
            logger.info(f"Added vip for user {user_id} for {days} days")
        except Exception as e:
            logger.error(f"Error adding vip: {e}")
        finally:
            conn.close()
    
    send_subscription_confirmation(user_id, "⭐ VIP", expiry)
    
    try:
        bot.send_message(OWNER_ID, f"✅ VIP added to user {user_id} for {days} days!")
    except:
        pass

# =============== SYSTEM STATS ===============

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

# =============== LOGIC FUNCTIONS ===============

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
    main_reply_markup = create_reply_keyboard_main_menu(user_id)
    try:
        if photo_file_id: bot.send_photo(chat_id, photo_file_id)
        bot.send_message(chat_id, welcome_msg_text, reply_markup=main_reply_markup, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Error sending welcome to {user_id}: {e}", exc_info=True)
        try: bot.send_message(chat_id, welcome_msg_text, reply_markup=main_reply_markup, parse_mode='Markdown')
        except Exception as fallback_e: logger.error(f"Fallback send_message failed for {user_id}: {fallback_e}")

def _logic_price_list(message):
    show_price_list(message.chat.id)

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
                     f"👤 Your Level: {user_level}")
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

def _logic_subscriptions_panel(message):
    if message.from_user.id not in admin_ids:
        bot.reply_to(message, "👑 Admin permissions required.")
        return
    bot.reply_to(message, "💳 **Subscription Management**\nUse inline buttons below.", reply_markup=create_subscription_menu(), parse_mode='Markdown')

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
        text = f"""📊 **System Statistics** 📊

💻 **CPU:** {stats['cpu']}%
🧠 **Memory:** {stats['memory_used']:.1f}GB / {stats['memory_total']:.1f}GB ({stats['memory_percent']}%)
💾 **Disk:** {stats['disk_used']:.1f}GB / {stats['disk_total']:.1f}GB ({stats['disk_percent']}%)

🤖 **Running Bots:** {stats['running_bots']}
👥 **Total Users:** {stats['total_users']}

⚡ **Response Time:** 10ms (Flash of Light)
💾 **RAM:** 500GB
📁 **Storage:** Unlimited

⏱ **Uptime:** {get_uptime()}"""
        bot.reply_to(message, text, parse_mode='Markdown')
    else:
        bot.reply_to(message, "❌ Failed to get system statistics.")

def _logic_bot_manager(message):
    if message.from_user.id not in admin_ids:
        bot.reply_to(message, "👑 Admin permissions required.")
        return
    bot.reply_to(message, "🖥️ **Bot Manager**\nManage all hosted bots.", reply_markup=create_bot_manager(), parse_mode='Markdown')

def _logic_list_all_bots(message):
    if message.from_user.id not in admin_ids:
        bot.reply_to(message, "👑 Admin permissions required.")
        return
    
    if not bot_scripts:
        bot.reply_to(message, "📋 No bots are currently running.")
        return
    
    text = "📋 **All Running Bots:**\n\n"
    for script_key, script_info in bot_scripts.items():
        owner_id = script_info.get('script_owner_id', 'Unknown')
        file_name = script_info.get('file_name', 'Unknown')
        pid = script_info.get('process', {}).pid if script_info.get('process') else 'N/A'
        start_time = script_info.get('start_time', datetime.now())
        uptime = datetime.now() - start_time
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        text += f"📁 `{file_name}`\n"
        text += f"👤 User: `{owner_id}`\n"
        text += f"🆔 PID: `{pid}`\n"
        text += f"⏱ Uptime: {hours}h {minutes}m {seconds}s\n\n"
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 Back to Bot Manager", callback_data='bot_manager'))
    bot.reply_to(message, text, reply_markup=markup, parse_mode='Markdown')

def _logic_toggle_auto_restart(message):
    if message.from_user.id not in admin_ids:
        bot.reply_to(message, "👑 Admin permissions required.")
        return
    
    settings = get_bot_settings()
    current = settings.get('auto_restart', 'True')
    new_value = 'False' if current.lower() == 'true' else 'True'
    
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute('UPDATE bot_settings SET setting_value = ? WHERE setting_key = ?', (new_value, 'auto_restart'))
        conn.commit()
        conn.close()
    
    status = "✅ Enabled" if new_value == 'True' else "❌ Disabled"
    bot.reply_to(message, f"🔄 Auto-Restart: {status}")

def _logic_clean_dead_bots(message):
    if message.from_user.id not in admin_ids:
        bot.reply_to(message, "👑 Admin permissions required.")
        return
    
    cleaned = 0
    for script_key, script_info in list(bot_scripts.items()):
        process = script_info.get('process')
        if process:
            try:
                proc = psutil.Process(process.pid)
                if not proc.is_running() or proc.status() == psutil.STATUS_ZOMBIE:
                    del bot_scripts[script_key]
                    cleaned += 1
            except psutil.NoSuchProcess:
                del bot_scripts[script_key]
                cleaned += 1
            except Exception as e:
                logger.error(f"Error cleaning {script_key}: {e}")
    
    bot.reply_to(message, f"🧹 Cleaned {cleaned} dead bot(s)!")

def _logic_broadcast_init(message):
    if message.from_user.id not in admin_ids:
        bot.reply_to(message, "👑 Admin permissions required.")
        return
    msg = bot.reply_to(message, "📢 Send message to broadcast to all active users.\n/cancel to abort.")
    bot.register_next_step_handler(msg, process_broadcast_message)

def _logic_toggle_lock_bot(message):
    if message.from_user.id not in admin_ids:
        bot.reply_to(message, "👑 Admin permissions required.")
        return
    global bot_locked
    bot_locked = not bot_locked
    status = "🔒 locked" if bot_locked else "🔓 unlocked"
    logger.warning(f"Bot {status} by Admin {message.from_user.id} via command/button.")
    bot.reply_to(message, f"Bot has been {status}.")

def _logic_admin_panel(message):
    if message.from_user.id not in admin_ids:
        bot.reply_to(message, "👑 Admin permissions required.")
        return
    bot.reply_to(message, "👑 **Admin Panel**\nManage admins & settings.", reply_markup=create_admin_panel(), parse_mode='Markdown')

def _logic_run_all_scripts(message_or_call):
    if isinstance(message_or_call, telebot.types.Message):
        admin_user_id = message_or_call.from_user.id
        admin_chat_id = message_or_call.chat.id
        reply_func = lambda text, **kwargs: bot.reply_to(message_or_call, text, **kwargs)
        admin_message_obj_for_script_runner = message_or_call
    elif isinstance(message_or_call, telebot.types.CallbackQuery):
        admin_user_id = message_or_call.from_user.id
        admin_chat_id = message_or_call.message.chat.id
        bot.answer_callback_query(message_or_call.id)
        reply_func = lambda text, **kwargs: bot.send_message(admin_chat_id, text, **kwargs)
        admin_message_obj_for_script_runner = message_or_call.message
    else:
        logger.error("Invalid argument for _logic_run_all_scripts")
        return

    if admin_user_id not in admin_ids:
        reply_func("👑 Admin permissions required.")
        return

    reply_func("🔄 Starting process to run all user scripts. This may take a while...")
    logger.info(f"Admin {admin_user_id} initiated 'run all scripts' from chat {admin_chat_id}.")

    started_count = 0; attempted_users = 0; skipped_files = 0; error_files_details = []

    all_user_files_snapshot = dict(user_files)

    for target_user_id, files_for_user in all_user_files_snapshot.items():
        if not files_for_user: continue
        attempted_users += 1
        logger.info(f"Processing scripts for user {target_user_id}...")
        user_folder = get_user_folder(target_user_id)

        for file_name, file_type in files_for_user:
            if not is_bot_running(target_user_id, file_name):
                file_path = os.path.join(user_folder, file_name)
                if os.path.exists(file_path):
                    logger.info(f"Admin {admin_user_id} attempting to start '{file_name}' ({file_type}) for user {target_user_id}.")
                    try:
                        if file_type == 'py':
                            threading.Thread(target=run_script, args=(file_path, target_user_id, user_folder, file_name, admin_message_obj_for_script_runner)).start()
                            started_count += 1
                        elif file_type == 'js':
                            threading.Thread(target=run_js_script, args=(file_path, target_user_id, user_folder, file_name, admin_message_obj_for_script_runner)).start()
                            started_count += 1
                        else:
                            logger.warning(f"Unknown file type '{file_type}' for {file_name} (user {target_user_id}). Skipping.")
                            error_files_details.append(f"`{file_name}` (User {target_user_id}) - Unknown type")
                            skipped_files += 1
                        time.sleep(0.7)
                    except Exception as e:
                        logger.error(f"Error queueing start for '{file_name}' (user {target_user_id}): {e}")
                        error_files_details.append(f"`{file_name}` (User {target_user_id}) - Start error")
                        skipped_files += 1
                else:
                    logger.warning(f"File '{file_name}' for user {target_user_id} not found at '{file_path}'. Skipping.")
                    error_files_details.append(f"`{file_name}` (User {target_user_id}) - File not found")
                    skipped_files += 1

    summary_msg = (f"✅ **All Users' Scripts - Processing Complete:**\n\n"
                   f"🔄 Attempted to start: {started_count} scripts.\n"
                   f"👥 Users processed: {attempted_users}.\n")
    if skipped_files > 0:
        summary_msg += f"⚠️ Skipped/Error files: {skipped_files}\n"
        if error_files_details:
             summary_msg += "📋 Details (first 5):\n" + "\n".join([f"  - {err}" for err in error_files_details[:5]])
             if len(error_files_details) > 5: summary_msg += "\n  ... and more (check logs)."

    reply_func(summary_msg, parse_mode='Markdown')
    logger.info(f"Run all scripts finished. Admin: {admin_user_id}. Started: {started_count}. Skipped/Errors: {skipped_files}")

def _logic_global_history(message):
    if message.from_user.id not in admin_ids:
        bot.reply_to(message, "👑 Admin permissions required.")
        return
    
    conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute('SELECT user_id, file_name, file_type, upload_time FROM global_file_history ORDER BY upload_time DESC LIMIT 50')
    history = c.fetchall()
    conn.close()
    
    if not history:
        bot.reply_to(message, "📂 No file history found.")
        return
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    for user_id, file_name, file_type, upload_time in history:
        btn_text = f"👤 {user_id} | 📁 {file_name} ({file_type})"
        markup.add(types.InlineKeyboardButton(btn_text, callback_data=f'view_file_{user_id}_{file_name}'))
    
    markup.add(types.InlineKeyboardButton("🔙 Back to Admin", callback_data='admin_panel'))
    bot.reply_to(message, "📂 **Global File History** (Last 50 files):", reply_markup=markup)

# =============== CHATGPT COMMAND ===============

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
    
    # Send typing indicator
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

# =============== MPX COMMAND ===============

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

@bot.message_handler(commands=['start', 'help'])
def command_send_welcome(message): _logic_send_welcome(message)

@bot.message_handler(commands=['status'])
def command_show_status(message): _logic_statistics(message)

@bot.message_handler(commands=['uptime'])
def command_uptime(message):
    _logic_uptime(message)

@bot.message_handler(commands=['ping'])
def ping(message):
    start_ping_time = time.time()
    msg = bot.reply_to(message, "🏓 Pong!")
    latency = round((time.time() - start_ping_time) * 1000, 2)
    uptime_str = get_uptime()
    bot.edit_message_text(f"🏓 Pong!\n📡 Latency: {latency} ms\n⏱ Uptime: {uptime_str}\n⚡ Response Time: 10ms",
                          message.chat.id, msg.message_id)

@bot.message_handler(commands=['price'])
def price_command(message):
    show_price_list(message.chat.id)

# =============== PRICE LIST BUTTON FIX ===============

@bot.message_handler(func=lambda message: message.text == "💲 Price List")
def price_list_button_handler(message):
    show_price_list(message.chat.id)

@bot.message_handler(func=lambda message: message.text == "🤖 ChatGPT")
def chatgpt_button_handler(message):
    bot.reply_to(message, "🤖 **ChatGPT**\n\nSend your query using:\n`/chatgpt Your question`\n`/gpt Your question`\n`/ai Your question`\n\nOr simply type `/mpx Your question`", parse_mode='Markdown')

# =============== ADMIN COMMANDS ===============

@bot.message_handler(commands=['admin'])
def admin_commands(message):
    if message.from_user.id not in admin_ids:
        bot.reply_to(message, "👑 Admin permissions required.")
        return
    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "📋 **Admin Commands:**\n"
                             "/admin prime <id> <time> <files> - Add Prime\n"
                             "/admin vip <id> <time> <files> - Add VIP\n"
                             "/admin ban <id> - Ban user\n"
                             "/admin unban <id> - Unban user\n"
                             "/admin host <id> <time> <files> - Add hosting\n"
                             "/admin remove <id> - Remove user's hosting\n"
                             "/admin stats - System stats")
        return
    command = args[1].lower()
    user_id = int(args[2]) if len(args) > 2 else None
    if command == "prime":
        if len(args) < 5:
            bot.reply_to(message, "Usage: /admin prime <user_id> <time> <files> e.g., /admin prime 123456789 100h 10f")
            return
        time_str = args[3]
        files = int(args[4].replace('f', ''))
        add_prime(user_id, time_str, files)
        bot.reply_to(message, f"✅ Prime added to user {user_id} for {time_str} with {files} files.")
    elif command == "vip":
        if len(args) < 5:
            bot.reply_to(message, "Usage: /admin vip <user_id> <time> <files> e.g., /admin vip 123456789 30d 10f")
            return
        time_str = args[3]
        files = int(args[4].replace('f', ''))
        add_vip(user_id, time_str, files)
        bot.reply_to(message, f"✅ VIP added to user {user_id} for {time_str} with {files} files.")
    elif command == "ban":
        if user_id is None:
            bot.reply_to(message, "Usage: /admin ban <user_id>")
            return
        add_ban(user_id)
        bot.reply_to(message, f"🚫 User {user_id} banned.")
    elif command == "unban":
        if user_id is None:
            bot.reply_to(message, "Usage: /admin unban <user_id>")
            return
        remove_ban(user_id)
        bot.reply_to(message, f"✅ User {user_id} unbanned.")
    elif command == "host":
        if len(args) < 5:
            bot.reply_to(message, "Usage: /admin host <user_id> <time> <files> e.g., /admin host 123456789 24h 10f")
            return
        time_str = args[3]
        files = int(args[4].replace('f', ''))
        add_hosting(user_id, time_str, files)
        bot.reply_to(message, f"✅ Hosting added to user {user_id} for {time_str} with {files} files.")
    elif command == "remove":
        if user_id is None:
            bot.reply_to(message, "Usage: /admin remove <user_id>")
            return
        remove_hosting(user_id)
        bot.reply_to(message, f"✅ Removed hosting for user {user_id}.")
    elif command == "stats":
        _logic_system_stats(message)
    else:
        bot.reply_to(message, "❌ Invalid admin command. Use prime, vip, ban, unban, host, remove, stats.")

@bot.message_handler(commands=['globalhistory'])
def global_file_history(message):
    _logic_global_history(message)

@bot.message_handler(commands=['botmanager'])
def bot_manager(message):
    _logic_bot_manager(message)

BUTTON_TEXT_TO_LOGIC = {
    "📢 Updates Channel": _logic_updates_channel,
    "📤 Upload File": _logic_upload_file,
    "📂 Check Files": _logic_check_files,
    "⚡ Bot Speed": _logic_bot_speed,
    "📞 Contact Owner": _logic_contact_owner,
    "📊 Statistics": _logic_statistics,
    "⏱ Uptime": _logic_uptime,
    "💳 Subscriptions": _logic_subscriptions_panel,
    "📢 Broadcast": _logic_broadcast_init,
    "🔒 Lock Bot": _logic_toggle_lock_bot,
    "🟢 Running All Code": _logic_run_all_scripts,
    "👑 Admin Panel": _logic_admin_panel,
    "💲 Price List": lambda m: show_price_list(m.chat.id),
    "📂 Global History": _logic_global_history,
    "🖥️ Bot Manager": _logic_bot_manager,
    "📊 System Stats": _logic_system_stats,
    "🤖 ChatGPT": chatgpt_button_handler
}

@bot.message_handler(func=lambda message: message.text in BUTTON_TEXT_TO_LOGIC)
def handle_button_text(message):
    logic_func = BUTTON_TEXT_TO_LOGIC.get(message.text)
    if logic_func: logic_func(message)
    else: logger.warning(f"Button text '{message.text}' matched but no logic func.")

@bot.message_handler(commands=['updateschannel'])
def command_updates_channel(message): _logic_updates_channel(message)
@bot.message_handler(commands=['uploadfile'])
def command_upload_file(message): _logic_upload_file(message)
@bot.message_handler(commands=['checkfiles'])
def command_check_files(message): _logic_check_files(message)
@bot.message_handler(commands=['botspeed'])
def command_bot_speed(message): _logic_bot_speed(message)
@bot.message_handler(commands=['contactowner'])
def command_contact_owner(message): _logic_contact_owner(message)
@bot.message_handler(commands=['subscriptions'])
def command_subscriptions(message): _logic_subscriptions_panel(message)
@bot.message_handler(commands=['statistics'])
def command_statistics(message): _logic_statistics(message)
@bot.message_handler(commands=['broadcast'])
def command_broadcast(message): _logic_broadcast_init(message)
@bot.message_handler(commands=['lockbot'])
def command_lock_bot(message): _logic_toggle_lock_bot(message)
@bot.message_handler(commands=['adminpanel'])
def command_admin_panel(message): _logic_admin_panel(message)
@bot.message_handler(commands=['runningallcode'])
def command_run_all_code(message): _logic_run_all_scripts(message)

# =============== FILE UPLOAD HANDLER ===============

@bot.message_handler(content_types=['document'])
def handle_file_upload_doc(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    doc = message.document
    logger.info(f"Doc from {user_id}: {doc.file_name} ({doc.mime_type}), Size: {doc.file_size}")

    if bot_locked and user_id not in admin_ids:
        bot.reply_to(message, "🔒 Bot locked, cannot accept files.")
        return

    if user_id in user_ban:
        bot.reply_to(message, "🚫 You are banned from using this bot.")
        return

    if not can_user_host(user_id):
        bot.reply_to(message, "⏰ Your hosting time has expired! Please contact admin.")
        return

    file_limit = get_user_file_limit(user_id)
    current_files = get_user_file_count(user_id)
    if current_files >= file_limit:
        limit_str = "Unlimited" if file_limit == float('inf') else str(file_limit)
        bot.reply_to(message, f"📁 File limit ({current_files}/{limit_str}) reached. Delete files via /checkfiles.")
        return

    file_name = doc.file_name
    if not file_name: bot.reply_to(message, "No file name. Ensure file has a name."); return
    file_ext = os.path.splitext(file_name)[1].lower()
    if file_ext not in ['.py', '.js', '.zip']:
        bot.reply_to(message, "❌ Unsupported type! Only `.py`, `.js`, `.zip` allowed.")
        return
    max_file_size = 20 * 1024 * 1024
    if doc.file_size > max_file_size:
        bot.reply_to(message, f"📁 File too large (Max: {max_file_size // 1024 // 1024} MB)."); return

    try:
        try:
            bot.forward_message(OWNER_ID, chat_id, message.message_id)
            bot.send_message(OWNER_ID, f"📁 File '{file_name}' from {message.from_user.first_name} (`{user_id}`)", parse_mode='Markdown')
        except Exception as e: logger.error(f"Failed to forward uploaded file to OWNER_ID {OWNER_ID}: {e}")

        download_wait_msg = bot.reply_to(message, f"📥 Downloading `{file_name}`...")
        file_info_tg_doc = bot.get_file(doc.file_id)
        downloaded_file_content = bot.download_file(file_info_tg_doc.file_path)
        bot.edit_message_text(f"📥 Downloaded `{file_name}`. Processing...", chat_id, download_wait_msg.message_id)
        logger.info(f"Downloaded {file_name} for user {user_id}")
        user_folder = get_user_folder(user_id)

        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute('INSERT INTO global_file_history (user_id, file_name, file_type, upload_time, file_path) VALUES (?, ?, ?, ?, ?)',
                  (user_id, file_name, file_ext[1:], datetime.now().isoformat(), os.path.join(user_folder, file_name)))
        conn.commit()
        conn.close()

        if file_ext == '.zip':
            handle_zip_file(downloaded_file_content, file_name, message)
        else:
            file_path = os.path.join(user_folder, file_name)
            with open(file_path, 'wb') as f: f.write(downloaded_file_content)
            logger.info(f"Saved single file to {file_path}")
            if file_ext == '.js': handle_js_file(file_path, user_id, user_folder, file_name, message)
            elif file_ext == '.py': handle_py_file(file_path, user_id, user_folder, file_name, message)
    except telebot.apihelper.ApiTelegramException as e:
         logger.error(f"Telegram API Error handling file for {user_id}: {e}", exc_info=True)
         if "file is too big" in str(e).lower():
              bot.reply_to(message, f"❌ Telegram API Error: File too large to download (~20MB limit).")
         else: bot.reply_to(message, f"❌ Telegram API Error: {str(e)}. Try later.")
    except Exception as e:
        logger.error(f"General error handling file for {user_id}: {e}", exc_info=True)
        bot.reply_to(message, f"❌ Unexpected error: {str(e)}")

# =============== MAIN CALLBACK HANDLER ===============

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    user_id = call.from_user.id
    data = call.data
    logger.info(f"Callback: User={user_id}, Data='{data}'")

    # =============== PRICE LIST - TOP PRIORITY ===============
    if data == 'price_list':
        bot.answer_callback_query(call.id, "💲 Loading Price List...")
        try:
            show_price_list(call.message.chat.id, call.message.message_id)
            return
        except Exception as e:
            logger.error(f"Price list error: {e}")
            bot.answer_callback_query(call.id, "❌ Error!", show_alert=True)
            return
    
    if data == 'show_prime_plans':
        bot.answer_callback_query(call.id, "🥇 Loading Prime Plans...")
        try:
            show_prime_plans(call.message.chat.id, call.message.message_id)
            return
        except Exception as e:
            logger.error(f"Prime plans error: {e}")
            bot.answer_callback_query(call.id, "❌ Error!", show_alert=True)
            return
    
    if data == 'show_vip_plans':
        bot.answer_callback_query(call.id, "⭐ Loading VIP Plans...")
        try:
            show_vip_plans(call.message.chat.id, call.message.message_id)
            return
        except Exception as e:
            logger.error(f"VIP plans error: {e}")
            bot.answer_callback_query(call.id, "❌ Error!", show_alert=True)
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
                show_plan_details(
                    call.message.chat.id, 
                    call.message.message_id,
                    "🥇 PRIME",
                    plan_name,
                    days,
                    plan_data['price'],
                    plan_data['qr']
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
                show_plan_details(
                    call.message.chat.id, 
                    call.message.message_id,
                    "⭐ VIP",
                    plan_name,
                    days,
                    plan_data['price'],
                    plan_data['qr']
                )
            else:
                bot.answer_callback_query(call.id, "❌ Plan not found!", show_alert=True)
            return
        except Exception as e:
            logger.error(f"Buy vip error: {e}")
            bot.answer_callback_query(call.id, "❌ Error!", show_alert=True)
            return
    
    if data == 'back_to_prime_plans':
        try:
            bot.answer_callback_query(call.id, "🔙 Back to Prime Plans")
            show_prime_plans(call.message.chat.id, call.message.message_id)
            return
        except Exception as e:
            logger.error(f"Back to prime error: {e}")
            bot.answer_callback_query(call.id, "❌ Error!", show_alert=True)
            return
    
    if data == 'back_to_vip_plans':
        try:
            bot.answer_callback_query(call.id, "🔙 Back to VIP Plans")
            show_vip_plans(call.message.chat.id, call.message.message_id)
            return
        except Exception as e:
            logger.error(f"Back to vip error: {e}")
            bot.answer_callback_query(call.id, "❌ Error!", show_alert=True)
            return

    # ... baaki code
    
    try:
        # =============== PAYMENT CALLBACKS ===============
        if data.startswith('pay_done_'):
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
        
        elif data == 'pay_reject':
            bot.answer_callback_query(call.id, "❌ Payment rejected!")
            bot.send_message(call.message.chat.id, 
                            f"❌ **Payment Rejected!**\n\n"
                            f"If you have any questions, contact: {YOUR_USERNAME}", parse_mode='Markdown')
            try:
                bot.delete_message(call.message.chat.id, call.message.message_id)
            except:
                pass
            return
        
        # =============== ADMIN PAYMENT CALLBACKS ===============
        elif data.startswith('add_prime_'):
            parts = data.split('_')
            target_user_id = int(parts[2])
            days = int(parts[3])
            
            if user_id not in admin_ids:
                bot.answer_callback_query(call.id, "👑 Admin only!", show_alert=True)
                return
            
            add_prime_to_user(target_user_id, days)
            bot.answer_callback_query(call.id, f"✅ Prime added to user {target_user_id}!")
            bot.edit_message_text(f"✅ Prime added to user {target_user_id} for {days} days!", 
                                call.message.chat.id, call.message.message_id)
            
            # Admin ko bhi notify karein
            try:
                bot.send_message(OWNER_ID, f"✅ Prime added to user {target_user_id} for {days} days by Admin {user_id}!")
            except:
                pass
            return
        
        elif data.startswith('add_vip_'):
            parts = data.split('_')
            target_user_id = int(parts[2])
            days = int(parts[3])
            
            if user_id not in admin_ids:
                bot.answer_callback_query(call.id, "👑 Admin only!", show_alert=True)
                return
            
            add_vip_to_user(target_user_id, days)
            bot.answer_callback_query(call.id, f"✅ VIP added to user {target_user_id}!")
            bot.edit_message_text(f"✅ VIP added to user {target_user_id} for {days} days!", 
                                call.message.chat.id, call.message.message_id)
            
            try:
                bot.send_message(OWNER_ID, f"✅ VIP added to user {target_user_id} for {days} days by Admin {user_id}!")
            except:
                pass
            return
        
        elif data.startswith('reject_payment_'):
            target_user_id = int(data.replace('reject_payment_', ''))
            
            if user_id not in admin_ids:
                bot.answer_callback_query(call.id, "👑 Admin only!", show_alert=True)
                return
            
            bot.answer_callback_query(call.id, f"❌ Payment rejected for user {target_user_id}!")
            bot.edit_message_text(f"❌ Payment rejected for user {target_user_id}!", 
                                call.message.chat.id, call.message.message_id)
            
            try:
                bot.send_message(OWNER_ID, f"❌ Payment rejected for user {target_user_id} by Admin {user_id}!")
            except:
                pass
            
            try:
                bot.send_message(target_user_id, 
                                f"❌ **Your payment was rejected!**\n\n"
                                f"Please contact admin: {YOUR_USERNAME}", parse_mode='Markdown')
            except:
                pass
            return

        # =============== ALL USERS BOTS (ADMIN) ===============
        elif data == 'all_users_bots':
            if user_id not in admin_ids:
                bot.answer_callback_query(call.id, "👑 Admin only!", show_alert=True)
                return
            
            bot.answer_callback_query(call.id, "👥 Loading all users' bots...")
            
            if not user_files:
                bot.send_message(call.message.chat.id, "📁 No users have uploaded any files yet.")
                return
            
            markup = types.InlineKeyboardMarkup(row_width=1)
            for uid, files in user_files.items():
                if files:
                    for file_name, file_type in files:
                        is_running = is_bot_running(uid, file_name)
                        status_icon = "🟢" if is_running else "🔴"
                        btn_text = f"{status_icon} User {uid}: {file_name} ({file_type})"
                        markup.add(types.InlineKeyboardButton(btn_text, callback_data=f'file_{uid}_{file_name}'))
            
            markup.add(types.InlineKeyboardButton("🔙 Back to Admin", callback_data='admin_panel'))
            bot.send_message(call.message.chat.id, "👥 **All Users' Bots:**\nClick to control any bot.", 
                            reply_markup=markup, parse_mode='Markdown')
            return

        # =============== BOT MANAGER CALLBACKS ===============
        elif data == 'bot_manager':
            admin_required_callback(call, _logic_bot_manager)
            return
        
        elif data == 'list_all_bots':
            admin_required_callback(call, _logic_list_all_bots)
            return
        
        elif data == 'toggle_auto_restart':
            admin_required_callback(call, _logic_toggle_auto_restart)
            return
        
        elif data == 'clean_dead_bots':
            admin_required_callback(call, _logic_clean_dead_bots)
            return
        
        elif data == 'system_stats':
            admin_required_callback(call, _logic_system_stats)
            return

        # =============== FILE MANAGEMENT CALLBACKS ===============
        elif data == 'upload':
            upload_callback(call)
        elif data == 'check_files':
            check_files_callback(call)
        elif data.startswith('file_'):
            file_control_callback(call)
        elif data.startswith('start_'):
            start_bot_callback(call)
        elif data.startswith('stop_'):
            stop_bot_callback(call)
        elif data.startswith('restart_'):
            restart_bot_callback(call)
        elif data.startswith('delete_'):
            delete_bot_callback(call)
        elif data.startswith('logs_'):
            logs_bot_callback(call)
        elif data.startswith('code_'):
            view_code_callback(call)
        elif data.startswith('view_file_'):
            view_global_file_callback(call)
        
        # =============== OTHER CALLBACKS ===============
        elif data == 'chatgpt':
            bot.answer_callback_query(call.id, "🤖 ChatGPT")
            bot.send_message(call.message.chat.id, 
                            "🤖 **ChatGPT**\n\n"
                            "Send your query using:\n"
                            "`/chatgpt Your question`\n"
                            "`/gpt Your question`\n"
                            "`/ai Your question`\n\n"
                            "Or simply type `/mpx Your question`", parse_mode='Markdown')
            return
        elif data == 'speed':
            speed_callback(call)
        elif data == 'back_to_main':
            back_to_main_callback(call)
        elif data.startswith('confirm_broadcast_'):
            handle_confirm_broadcast(call)
        elif data == 'cancel_broadcast':
            handle_cancel_broadcast(call)
        elif data == 'subscription':
            admin_required_callback(call, subscription_management_callback)
        elif data == 'stats':
            stats_callback(call)
        elif data == 'lock_bot':
            admin_required_callback(call, lock_bot_callback)
        elif data == 'unlock_bot':
            admin_required_callback(call, unlock_bot_callback)
        elif data == 'run_all_scripts':
            admin_required_callback(call, run_all_scripts_callback)
        elif data == 'broadcast':
            admin_required_callback(call, broadcast_init_callback)
        elif data == 'admin_panel':
            admin_required_callback(call, admin_panel_callback)
        elif data == 'free_settings':
            admin_required_callback(call, free_settings_callback)
        elif data.startswith('toggle_free_'):
            admin_required_callback(call, toggle_free_user_callback)
        elif data == 'set_free_files':
            admin_required_callback(call, set_free_files_callback)
        elif data == 'set_free_hours':
            admin_required_callback(call, set_free_hours_callback)
        elif data == 'add_admin':
            owner_required_callback(call, add_admin_init_callback)
        elif data == 'remove_admin':
            owner_required_callback(call, remove_admin_init_callback)
        elif data == 'list_admins':
            admin_required_callback(call, list_admins_callback)
        elif data == 'add_subscription':
            admin_required_callback(call, add_subscription_init_callback)
        elif data == 'remove_subscription':
            admin_required_callback(call, remove_subscription_init_callback)
        elif data == 'check_subscription':
            admin_required_callback(call, check_subscription_init_callback)
        elif data == 'mpx_ai':
            bot.answer_callback_query(call.id)
            bot.send_message(call.message.chat.id, "🤖 Please send your query using the /mpx command followed by your question.\nExample: `/mpx What is AI?`", parse_mode='Markdown')
        elif data == 'uptime':
            bot.answer_callback_query(call.id)
            uptime_str = get_uptime()
            bot.send_message(call.message.chat.id, f"⏱ Bot Uptime: `{uptime_str}`", parse_mode='Markdown')
        elif data == 'global_history':
            admin_required_callback(call, global_history_callback)
        else:
            bot.answer_callback_query(call.id, "❌ Unknown action.")
            logger.warning(f"Unhandled callback data: {data} from user {user_id}")
    except Exception as e:
        logger.error(f"Error handling callback '{data}' for {user_id}: {e}", exc_info=True)
        try:
            bot.answer_callback_query(call.id, "❌ Error processing request.", show_alert=True)
        except Exception as e_ans:
            logger.error(f"Failed to answer callback after error: {e_ans}")

# =============== HELPER CALLBACK FUNCTIONS ===============

def admin_required_callback(call, func_to_run):
    if call.from_user.id not in admin_ids:
        bot.answer_callback_query(call.id, "👑 Admin permissions required.", show_alert=True)
        return
    func_to_run(call)

def owner_required_callback(call, func_to_run):
    if call.from_user.id != OWNER_ID:
        bot.answer_callback_query(call.id, "👑 Owner permissions required.", show_alert=True)
        return
    func_to_run(call)

def upload_callback(call):
    user_id = call.from_user.id
    if user_id in user_ban:
        bot.answer_callback_query(call.id, "🚫 You are banned.", show_alert=True)
        return
    if not can_user_host(user_id):
        bot.answer_callback_query(call.id, "⏰ Hosting expired!", show_alert=True)
        return
    file_limit = get_user_file_limit(user_id)
    current_files = get_user_file_count(user_id)
    if current_files >= file_limit:
        limit_str = "Unlimited" if file_limit == float('inf') else str(file_limit)
        bot.answer_callback_query(call.id, f"📁 File limit ({current_files}/{limit_str}) reached.", show_alert=True)
        return
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, "📤 Send your Python (`.py`), JS (`.js`), or ZIP (`.zip`) file.")

def check_files_callback(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    user_files_list = user_files.get(user_id, [])
    if not user_files_list:
        bot.answer_callback_query(call.id, "📁 No files uploaded.", show_alert=True)
        try:
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🔙 Back to Main", callback_data='back_to_main'))
            bot.edit_message_text("📁 Your files:\n\n(No files uploaded)", chat_id, call.message.message_id, reply_markup=markup)
        except Exception as e: logger.error(f"Error editing msg for empty file list: {e}")
        return
    bot.answer_callback_query(call.id)
    markup = types.InlineKeyboardMarkup(row_width=1)
    for file_name, file_type in sorted(user_files_list):
        is_running = is_bot_running(user_id, file_name)
        status_icon = "🟢 Running" if is_running else "🔴 Stopped"
        btn_text = f"{file_name} ({file_type}) - {status_icon}"
        markup.add(types.InlineKeyboardButton(btn_text, callback_data=f'file_{user_id}_{file_name}'))
    markup.add(types.InlineKeyboardButton("🔙 Back to Main", callback_data='back_to_main'))
    try:
        bot.edit_message_text("📁 Your files:\nClick to manage.", chat_id, call.message.message_id, reply_markup=markup, parse_mode='Markdown')
    except telebot.apihelper.ApiTelegramException as e:
         if "message is not modified" in str(e): logger.warning("Msg not modified (files).")
         else: logger.error(f"Error editing msg for file list: {e}")
    except Exception as e: logger.error(f"Unexpected error editing msg for file list: {e}", exc_info=True)

def file_control_callback(call):
    try:
        _, script_owner_id_str, file_name = call.data.split('_', 2)
        script_owner_id = int(script_owner_id_str)
        requesting_user_id = call.from_user.id

        # ✅ FIX: Admin can control ANY user's bot
        if not (requesting_user_id == script_owner_id or requesting_user_id in admin_ids):
            logger.warning(f"User {requesting_user_id} tried to access file '{file_name}' of user {script_owner_id} without permission.")
            bot.answer_callback_query(call.id, "🔒 You can only manage your own files.", show_alert=True)
            check_files_callback(call)
            return

        user_files_list = user_files.get(script_owner_id, [])
        if not any(f[0] == file_name for f in user_files_list):
            bot.answer_callback_query(call.id, "📁 File not found.", show_alert=True)
            check_files_callback(call)
            return

        bot.answer_callback_query(call.id)
        is_running = is_bot_running(script_owner_id, file_name)
        status_text = '🟢 Running' if is_running else '🔴 Stopped'
        file_type = next((f[1] for f in user_files_list if f[0] == file_name), '?')
        
        # Show admin tag if admin is viewing
        admin_tag = " (👑 Admin View)" if requesting_user_id in admin_ids and requesting_user_id != script_owner_id else ""
        
        try:
            bot.edit_message_text(
                f"📁 **Controls for:** `{file_name}` ({file_type}){admin_tag}\n"
                f"👤 User: `{script_owner_id}`\n"
                f"📊 Status: {status_text}",
                call.message.chat.id, call.message.message_id,
                reply_markup=create_control_buttons(script_owner_id, file_name, is_running),
                parse_mode='Markdown'
            )
        except telebot.apihelper.ApiTelegramException as e:
             if "message is not modified" in str(e): logger.warning(f"Msg not modified (controls for {file_name})")
             else: raise
    except (ValueError, IndexError) as ve:
        logger.error(f"Error parsing file control callback: {ve}. Data: '{call.data}'")
        bot.answer_callback_query(call.id, "❌ Error: Invalid action data.", show_alert=True)
    except Exception as e:
        logger.error(f"Error in file_control_callback for data '{call.data}': {e}", exc_info=True)
        bot.answer_callback_query(call.id, "❌ An error occurred.", show_alert=True)

def view_code_callback(call):
    try:
        _, script_owner_id_str, file_name = call.data.split('_', 2)
        script_owner_id = int(script_owner_id_str)
        requesting_user_id = call.from_user.id

        if not (requesting_user_id == script_owner_id or requesting_user_id in admin_ids):
            bot.answer_callback_query(call.id, "🔒 Permission denied.", show_alert=True)
            return

        user_files_list = user_files.get(script_owner_id, [])
        if not any(f[0] == file_name for f in user_files_list):
            bot.answer_callback_query(call.id, "📁 File not found.", show_alert=True)
            return

        user_folder = get_user_folder(script_owner_id)
        file_path = os.path.join(user_folder, file_name)
        
        if not os.path.exists(file_path):
            bot.answer_callback_query(call.id, "❌ File not found on disk.", show_alert=True)
            return

        bot.answer_callback_query(call.id)
        content = get_file_content(file_path)
        if content is None:
            bot.send_message(call.message.chat.id, f"❌ Could not read file `{file_name}`.")
            return
        
        if len(content) > 4000:
            content = content[:4000] + "\n\n... (truncated)"
        
        bot.send_message(call.message.chat.id, 
                        f"📄 **Code for:** `{file_name}`\n```python\n{content}\n```", 
                        parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Error in view_code_callback: {e}", exc_info=True)
        bot.answer_callback_query(call.id, "❌ Error viewing code.", show_alert=True)

def view_global_file_callback(call):
    try:
        _, user_id_str, file_name = call.data.split('_', 2)
        target_user_id = int(user_id_str)
        requesting_user_id = call.from_user.id

        if requesting_user_id not in admin_ids:
            bot.answer_callback_query(call.id, "👑 Admin only.", show_alert=True)
            return

        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute('SELECT file_path FROM global_file_history WHERE user_id = ? AND file_name = ? ORDER BY upload_time DESC LIMIT 1', 
                  (target_user_id, file_name))
        result = c.fetchone()
        conn.close()

        if not result:
            bot.answer_callback_query(call.id, "❌ File not found in history.", show_alert=True)
            return

        file_path = result[0]
        if not os.path.exists(file_path):
            bot.answer_callback_query(call.id, "❌ File not found on disk.", show_alert=True)
            return

        bot.answer_callback_query(call.id, f"📄 Viewing file: {file_name}")
        content = get_file_content(file_path)
        
        if content is None:
            bot.send_message(call.message.chat.id, f"❌ Could not read file `{file_name}`.")
            return
        
        if len(content) > 4000:
            content = content[:4000] + "\n\n... (truncated)"
        
        bot.send_message(call.message.chat.id, 
                        f"📄 **Global File:** `{file_name}` (User: `{target_user_id}`)\n```python\n{content}\n```", 
                        parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Error in view_global_file_callback: {e}", exc_info=True)
        bot.answer_callback_query(call.id, "❌ Error viewing file.", show_alert=True)

def start_bot_callback(call):
    try:
        _, script_owner_id_str, file_name = call.data.split('_', 2)
        script_owner_id = int(script_owner_id_str)
        requesting_user_id = call.from_user.id
        chat_id_for_reply = call.message.chat.id

        logger.info(f"Start request: Requester={requesting_user_id}, Owner={script_owner_id}, File='{file_name}'")

        if not (requesting_user_id == script_owner_id or requesting_user_id in admin_ids):
            bot.answer_callback_query(call.id, "🔒 Permission denied to start this script.", show_alert=True); return

        if requesting_user_id in user_ban:
            bot.answer_callback_query(call.id, "🚫 You are banned.", show_alert=True)
            return

        if not can_user_host(script_owner_id):
            bot.answer_callback_query(call.id, "⏰ Hosting expired!", show_alert=True)
            return

        user_files_list = user_files.get(script_owner_id, [])
        file_info = next((f for f in user_files_list if f[0] == file_name), None)
        if not file_info:
            bot.answer_callback_query(call.id, "📁 File not found.", show_alert=True); check_files_callback(call); return

        file_type = file_info[1]
        user_folder = get_user_folder(script_owner_id)
        file_path = os.path.join(user_folder, file_name)

        if not os.path.exists(file_path):
            bot.answer_callback_query(call.id, f"❌ File `{file_name}` missing! Re-upload.", show_alert=True)
            remove_user_file_db(script_owner_id, file_name); check_files_callback(call); return

        if is_bot_running(script_owner_id, file_name):
            bot.answer_callback_query(call.id, f"🤖 Script '{file_name}' already running.", show_alert=True)
            try: bot.edit_message_reply_markup(chat_id_for_reply, call.message.message_id, reply_markup=create_control_buttons(script_owner_id, file_name, True))
            except Exception as e: logger.error(f"Error updating buttons (already running): {e}")
            return

        bot.answer_callback_query(call.id, f"🔄 Starting {file_name}...")

        if file_type == 'py':
            threading.Thread(target=run_script, args=(file_path, script_owner_id, user_folder, file_name, call.message)).start()
        elif file_type == 'js':
            threading.Thread(target=run_js_script, args=(file_path, script_owner_id, user_folder, file_name, call.message)).start()
        else:
             bot.send_message(chat_id_for_reply, f"❌ Unknown file type '{file_type}' for '{file_name}'."); return

        time.sleep(1.5)
        is_now_running = is_bot_running(script_owner_id, file_name)
        status_text = '🟢 Running' if is_now_running else '🔴 Starting (or failed, check logs)'
        try:
            bot.edit_message_text(
                f"📁 **Controls for:** `{file_name}` ({file_type})\n"
                f"👤 User: `{script_owner_id}`\n"
                f"📊 Status: {status_text}",
                chat_id_for_reply, call.message.message_id,
                reply_markup=create_control_buttons(script_owner_id, file_name, is_now_running), parse_mode='Markdown'
            )
        except telebot.apihelper.ApiTelegramException as e:
             if "message is not modified" in str(e): logger.warning(f"Msg not modified after starting {file_name}")
             else: raise
    except (ValueError, IndexError) as e:
        logger.error(f"Error parsing start callback '{call.data}': {e}")
        bot.answer_callback_query(call.id, "❌ Invalid start command.", show_alert=True)
    except Exception as e:
        logger.error(f"Error in start_bot_callback for '{call.data}': {e}", exc_info=True)
        bot.answer_callback_query(call.id, "❌ Error starting script.", show_alert=True)
        try:
            _, script_owner_id_err_str, file_name_err = call.data.split('_', 2)
            script_owner_id_err = int(script_owner_id_err_str)
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=create_control_buttons(script_owner_id_err, file_name_err, False))
        except Exception as e_btn: logger.error(f"Failed to update buttons after start error: {e_btn}")

def stop_bot_callback(call):
    try:
        _, script_owner_id_str, file_name = call.data.split('_', 2)
        script_owner_id = int(script_owner_id_str)
        requesting_user_id = call.from_user.id
        chat_id_for_reply = call.message.chat.id

        logger.info(f"Stop request: Requester={requesting_user_id}, Owner={script_owner_id}, File='{file_name}'")
        if not (requesting_user_id == script_owner_id or requesting_user_id in admin_ids):
            bot.answer_callback_query(call.id, "🔒 Permission denied.", show_alert=True); return

        user_files_list = user_files.get(script_owner_id, [])
        file_info = next((f for f in user_files_list if f[0] == file_name), None)
        if not file_info:
            bot.answer_callback_query(call.id, "📁 File not found.", show_alert=True); check_files_callback(call); return

        file_type = file_info[1]
        script_key = f"{script_owner_id}_{file_name}"

        if not is_bot_running(script_owner_id, file_name):
            bot.answer_callback_query(call.id, f"🤖 Script '{file_name}' already stopped.", show_alert=True)
            try:
                 bot.edit_message_text(
                     f"📁 **Controls for:** `{file_name}` ({file_type})\n"
                     f"👤 User: `{script_owner_id}`\n"
                     f"📊 Status: 🔴 Stopped",
                     chat_id_for_reply, call.message.message_id,
                     reply_markup=create_control_buttons(script_owner_id, file_name, False), parse_mode='Markdown')
            except Exception as e: logger.error(f"Error updating buttons (already stopped): {e}")
            return

        bot.answer_callback_query(call.id, f"⏹ Stopping {file_name}...")
        process_info = bot_scripts.get(script_key)
        if process_info:
            kill_process_tree(process_info)
            if script_key in bot_scripts: del bot_scripts[script_key]; logger.info(f"Removed {script_key} from running after stop.")
        else: logger.warning(f"Script {script_key} running by psutil but not in bot_scripts dict.")

        try:
            bot.edit_message_text(
                f"📁 **Controls for:** `{file_name}` ({file_type})\n"
                f"👤 User: `{script_owner_id}`\n"
                f"📊 Status: 🔴 Stopped",
                chat_id_for_reply, call.message.message_id,
                reply_markup=create_control_buttons(script_owner_id, file_name, False), parse_mode='Markdown'
            )
        except telebot.apihelper.ApiTelegramException as e:
             if "message is not modified" in str(e): logger.warning(f"Msg not modified after stopping {file_name}")
             else: raise
    except (ValueError, IndexError) as e:
        logger.error(f"Error parsing stop callback '{call.data}': {e}")
        bot.answer_callback_query(call.id, "❌ Invalid stop command.", show_alert=True)
    except Exception as e:
        logger.error(f"Error in stop_bot_callback for '{call.data}': {e}", exc_info=True)
        bot.answer_callback_query(call.id, "❌ Error stopping script.", show_alert=True)

def restart_bot_callback(call):
    try:
        _, script_owner_id_str, file_name = call.data.split('_', 2)
        script_owner_id = int(script_owner_id_str)
        requesting_user_id = call.from_user.id
        chat_id_for_reply = call.message.chat.id

        logger.info(f"Restart: Requester={requesting_user_id}, Owner={script_owner_id}, File='{file_name}'")
        if not (requesting_user_id == script_owner_id or requesting_user_id in admin_ids):
            bot.answer_callback_query(call.id, "🔒 Permission denied.", show_alert=True); return

        user_files_list = user_files.get(script_owner_id, [])
        file_info = next((f for f in user_files_list if f[0] == file_name), None)
        if not file_info:
            bot.answer_callback_query(call.id, "📁 File not found.", show_alert=True); check_files_callback(call); return

        file_type = file_info[1]; user_folder = get_user_folder(script_owner_id)
        file_path = os.path.join(user_folder, file_name); script_key = f"{script_owner_id}_{file_name}"

        if not os.path.exists(file_path):
            bot.answer_callback_query(call.id, f"❌ File `{file_name}` missing! Re-upload.", show_alert=True)
            remove_user_file_db(script_owner_id, file_name)
            if script_key in bot_scripts: del bot_scripts[script_key]
            check_files_callback(call); return

        bot.answer_callback_query(call.id, f"🔄 Restarting {file_name}...")
        if is_bot_running(script_owner_id, file_name):
            logger.info(f"Restart: Stopping existing {script_key}...")
            process_info = bot_scripts.get(script_key)
            if process_info: kill_process_tree(process_info)
            if script_key in bot_scripts: del bot_scripts[script_key]
            time.sleep(1.5)

        logger.info(f"Restart: Starting script {script_key}...")
        if file_type == 'py':
            threading.Thread(target=run_script, args=(file_path, script_owner_id, user_folder, file_name, call.message)).start()
        elif file_type == 'js':
            threading.Thread(target=run_js_script, args=(file_path, script_owner_id, user_folder, file_name, call.message)).start()
        else:
             bot.send_message(chat_id_for_reply, f"❌ Unknown type '{file_type}' for '{file_name}'."); return

        time.sleep(1.5)
        is_now_running = is_bot_running(script_owner_id, file_name)
        status_text = '🟢 Running' if is_now_running else '🔴 Starting (or failed)'
        try:
            bot.edit_message_text(
                f"📁 **Controls for:** `{file_name}` ({file_type})\n"
                f"👤 User: `{script_owner_id}`\n"
                f"📊 Status: {status_text}",
                chat_id_for_reply, call.message.message_id,
                reply_markup=create_control_buttons(script_owner_id, file_name, is_now_running), parse_mode='Markdown'
            )
        except telebot.apihelper.ApiTelegramException as e:
             if "message is not modified" in str(e): logger.warning(f"Msg not modified (restart {file_name})")
             else: raise
    except (ValueError, IndexError) as e:
        logger.error(f"Error parsing restart callback '{call.data}': {e}")
        bot.answer_callback_query(call.id, "❌ Invalid restart command.", show_alert=True)
    except Exception as e:
        logger.error(f"Error in restart_bot_callback for '{call.data}': {e}", exc_info=True)
        bot.answer_callback_query(call.id, "❌ Error restarting.", show_alert=True)
        try:
            _, script_owner_id_err_str, file_name_err = call.data.split('_', 2)
            script_owner_id_err = int(script_owner_id_err_str)
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=create_control_buttons(script_owner_id_err, file_name_err, False))
        except Exception as e_btn: logger.error(f"Failed to update buttons after restart error: {e_btn}")

def delete_bot_callback(call):
    try:
        _, script_owner_id_str, file_name = call.data.split('_', 2)
        script_owner_id = int(script_owner_id_str)
        requesting_user_id = call.from_user.id
        chat_id_for_reply = call.message.chat.id

        logger.info(f"Delete: Requester={requesting_user_id}, Owner={script_owner_id}, File='{file_name}'")
        if not (requesting_user_id == script_owner_id or requesting_user_id in admin_ids):
            bot.answer_callback_query(call.id, "🔒 Permission denied.", show_alert=True); return

        user_files_list = user_files.get(script_owner_id, [])
        if not any(f[0] == file_name for f in user_files_list):
            bot.answer_callback_query(call.id, "📁 File not found.", show_alert=True); check_files_callback(call); return

        bot.answer_callback_query(call.id, f"🗑 Deleting {file_name}...")
        script_key = f"{script_owner_id}_{file_name}"
        if is_bot_running(script_owner_id, file_name):
            logger.info(f"Delete: Stopping {script_key}...")
            process_info = bot_scripts.get(script_key)
            if process_info: kill_process_tree(process_info)
            if script_key in bot_scripts: del bot_scripts[script_key]
            time.sleep(0.5)

        user_folder = get_user_folder(script_owner_id)
        file_path = os.path.join(user_folder, file_name)
        log_path = os.path.join(user_folder, f"{os.path.splitext(file_name)[0]}.log")
        deleted_disk = []
        if os.path.exists(file_path):
            try: os.remove(file_path); deleted_disk.append(file_name); logger.info(f"Deleted file: {file_path}")
            except OSError as e: logger.error(f"Error deleting {file_path}: {e}")
        if os.path.exists(log_path):
            try: os.remove(log_path); deleted_disk.append(os.path.basename(log_path)); logger.info(f"Deleted log: {log_path}")
            except OSError as e: logger.error(f"Error deleting log {log_path}: {e}")

        remove_user_file_db(script_owner_id, file_name)
        deleted_str = ", ".join(f"`{f}`" for f in deleted_disk) if deleted_disk else "associated files"
        try:
            bot.edit_message_text(
                f"🗑 **File Deleted:** `{file_name}` (User `{script_owner_id}`)\n"
                f"📁 Removed: {deleted_str}",
                chat_id_for_reply, call.message.message_id, reply_markup=None, parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"Error editing msg after delete: {e}")
            bot.send_message(chat_id_for_reply, f"🗑 File `{file_name}` deleted.", parse_mode='Markdown')
    except (ValueError, IndexError) as e:
        logger.error(f"Error parsing delete callback '{call.data}': {e}")
        bot.answer_callback_query(call.id, "❌ Invalid delete command.", show_alert=True)
    except Exception as e:
        logger.error(f"Error in delete_bot_callback for '{call.data}': {e}", exc_info=True)
        bot.answer_callback_query(call.id, "❌ Error deleting.", show_alert=True)

def logs_bot_callback(call):
    try:
        _, script_owner_id_str, file_name = call.data.split('_', 2)
        script_owner_id = int(script_owner_id_str)
        requesting_user_id = call.from_user.id
        chat_id_for_reply = call.message.chat.id

        logger.info(f"Logs: Requester={requesting_user_id}, Owner={script_owner_id}, File='{file_name}'")
        if not (requesting_user_id == script_owner_id or requesting_user_id in admin_ids):
            bot.answer_callback_query(call.id, "🔒 Permission denied.", show_alert=True); return

        user_files_list = user_files.get(script_owner_id, [])
        if not any(f[0] == file_name for f in user_files_list):
            bot.answer_callback_query(call.id, "📁 File not found.", show_alert=True); check_files_callback(call); return

        user_folder = get_user_folder(script_owner_id)
        log_path = os.path.join(user_folder, f"{os.path.splitext(file_name)[0]}.log")
        if not os.path.exists(log_path):
            bot.answer_callback_query(call.id, f"📜 No logs for '{file_name}'.", show_alert=True); return

        bot.answer_callback_query(call.id)
        try:
            log_content = get_last_log_lines(log_path, 50)
            
            if len(log_content) > 4000:
                log_content = log_content[-4000:]
                first_nl = log_content.find('\n')
                if first_nl != -1:
                    log_content = "...\n" + log_content[first_nl+1:]
                else:
                    log_content = "...\n" + log_content
            
            if not log_content.strip():
                log_content = "(No visible content)"

            bot.send_message(chat_id_for_reply, 
                            f"📜 **Logs for:** `{file_name}` (User `{script_owner_id}`)\n```\n{log_content}\n```", 
                            parse_mode='Markdown')
        except Exception as e:
            logger.error(f"Error reading/sending log {log_path}: {e}", exc_info=True)
            bot.send_message(chat_id_for_reply, f"❌ Error reading log for `{file_name}`.")
    except (ValueError, IndexError) as e:
        logger.error(f"Error parsing logs callback '{call.data}': {e}")
        bot.answer_callback_query(call.id, "❌ Invalid logs command.", show_alert=True)
    except Exception as e:
        logger.error(f"Error in logs_bot_callback for '{call.data}': {e}", exc_info=True)
        bot.answer_callback_query(call.id, "❌ Error fetching logs.", show_alert=True)

def speed_callback(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    start_cb_ping_time = time.time()
    try:
        bot.edit_message_text("⚡ Testing speed...", chat_id, call.message.message_id)
        bot.send_chat_action(chat_id, 'typing')
        response_time = round((time.time() - start_cb_ping_time) * 1000, 2)
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
                     f"👤 Your Level: {user_level}")
        bot.answer_callback_query(call.id)
        bot.edit_message_text(speed_msg, chat_id, call.message.message_id, reply_markup=create_main_menu_inline(user_id), parse_mode='Markdown')
    except Exception as e:
         logger.error(f"Error during speed test (cb): {e}", exc_info=True)
         bot.answer_callback_query(call.id, "❌ Error in speed test.", show_alert=True)
         try: bot.edit_message_text("Main Menu", chat_id, call.message.message_id, reply_markup=create_main_menu_inline(user_id))
         except Exception: pass

def back_to_main_callback(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
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

    main_menu_text = (f"🌟 **Welcome back, {call.from_user.first_name}!** 🌟\n\n"
                      f"🆔 ID: `{user_id}`\n"
                      f"📊 Status: {user_status}{expiry_info}\n"
                      f"📁 Files: {current_files} / {limit_str}\n\n"
                      f"💡 Use buttons or type commands.")
    try:
        bot.answer_callback_query(call.id)
        bot.edit_message_text(main_menu_text, chat_id, call.message.message_id,
                              reply_markup=create_main_menu_inline(user_id), parse_mode='Markdown')
    except telebot.apihelper.ApiTelegramException as e:
         if "message is not modified" in str(e): logger.warning("Msg not modified (back_to_main).")
         else: logger.error(f"API error on back_to_main: {e}")
    except Exception as e: logger.error(f"Error handling back_to_main: {e}", exc_info=True)

def subscription_management_callback(call):
    bot.answer_callback_query(call.id)
    try:
        bot.edit_message_text("💳 **Subscription Management**\nSelect action:",
                              call.message.chat.id, call.message.message_id, reply_markup=create_subscription_menu(), parse_mode='Markdown')
    except Exception as e: logger.error(f"Error showing sub menu: {e}")

def stats_callback(call):
    bot.answer_callback_query(call.id)
    _logic_statistics(call.message)
    try:
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                                      reply_markup=create_main_menu_inline(call.from_user.id))
    except Exception as e:
        logger.error(f"Error updating menu after stats_callback: {e}")

def lock_bot_callback(call):
    global bot_locked; bot_locked = True
    logger.warning(f"Bot locked by Admin {call.from_user.id}")
    bot.answer_callback_query(call.id, "🔒 Bot locked.")
    try: bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=create_main_menu_inline(call.from_user.id))
    except Exception as e: logger.error(f"Error updating menu (lock): {e}")

def unlock_bot_callback(call):
    global bot_locked; bot_locked = False
    logger.warning(f"Bot unlocked by Admin {call.from_user.id}")
    bot.answer_callback_query(call.id, "🔓 Bot unlocked.")
    try: bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=create_main_menu_inline(call.from_user.id))
    except Exception as e: logger.error(f"Error updating menu (unlock): {e}")

def run_all_scripts_callback(call):
    _logic_run_all_scripts(call)

def broadcast_init_callback(call):
    bot.answer_callback_query(call.id)
    msg = bot.send_message(call.message.chat.id, "📢 Send message to broadcast.\n/cancel to abort.")
    bot.register_next_step_handler(msg, process_broadcast_message)

def process_broadcast_message(message):
    user_id = message.from_user.id
    if user_id not in admin_ids: bot.reply_to(message, "👑 Not authorized."); return
    if message.text and message.text.lower() == '/cancel': bot.reply_to(message, "❌ Broadcast cancelled."); return

    broadcast_content = message.text
    if not broadcast_content and not (message.photo or message.video or message.document or message.sticker or message.voice or message.audio):
         bot.reply_to(message, "❌ Cannot broadcast empty message. Send text or media, or /cancel.")
         msg = bot.send_message(message.chat.id, "📢 Send broadcast message or /cancel.")
         bot.register_next_step_handler(msg, process_broadcast_message)
         return

    target_count = len(active_users)
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton("✅ Confirm & Send", callback_data=f"confirm_broadcast_{message.message_id}"),
               types.InlineKeyboardButton("❌ Cancel", callback_data="cancel_broadcast"))

    preview_text = broadcast_content[:1000].strip() if broadcast_content else "(Media message)"
    bot.reply_to(message, f"📢 **Confirm Broadcast:**\n\n```\n{preview_text}\n```\n"
                          f"👥 To **{target_count}** users. Sure?", reply_markup=markup, parse_mode='Markdown')

def handle_confirm_broadcast(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    if user_id not in admin_ids: bot.answer_callback_query(call.id, "👑 Admin only.", show_alert=True); return
    try:
        original_message = call.message.reply_to_message
        if not original_message: raise ValueError("Could not retrieve original message.")

        broadcast_text = None
        broadcast_photo_id = None
        broadcast_video_id = None

        if original_message.text:
            broadcast_text = original_message.text
        elif original_message.photo:
            broadcast_photo_id = original_message.photo[-1].file_id
        elif original_message.video:
            broadcast_video_id = original_message.video.file_id
        else:
            raise ValueError("Message has no text or supported media for broadcast.")

        bot.answer_callback_query(call.id, "📢 Starting broadcast...")
        bot.edit_message_text(f"📢 Broadcasting to {len(active_users)} users...",
                              chat_id, call.message.message_id, reply_markup=None)
        thread = threading.Thread(target=execute_broadcast, args=(
            broadcast_text, broadcast_photo_id, broadcast_video_id,
            original_message.caption if (broadcast_photo_id or broadcast_video_id) else None,
            chat_id))
        thread.start()
    except ValueError as ve:
        logger.error(f"Error retrieving msg for broadcast confirm: {ve}")
        bot.edit_message_text(f"❌ Error starting broadcast: {ve}", chat_id, call.message.message_id, reply_markup=None)
    except Exception as e:
        logger.error(f"Error in handle_confirm_broadcast: {e}", exc_info=True)
        bot.edit_message_text("❌ Unexpected error during broadcast confirm.", chat_id, call.message.message_id, reply_markup=None)

def handle_cancel_broadcast(call):
    bot.answer_callback_query(call.id, "❌ Broadcast cancelled.")
    bot.delete_message(call.message.chat.id, call.message.message_id)
    if call.message.reply_to_message:
        try: bot.delete_message(call.message.chat.id, call.message.reply_to_message.message_id)
        except: pass

def execute_broadcast(broadcast_text, photo_id, video_id, caption, admin_chat_id):
    sent_count = 0; failed_count = 0; blocked_count = 0
    start_exec_time = time.time()
    users_to_broadcast = list(active_users); total_users = len(users_to_broadcast)
    logger.info(f"Executing broadcast to {total_users} users.")
    batch_size = 25; delay_batches = 1.5

    for i, user_id_bc in enumerate(users_to_broadcast):
        try:
            if broadcast_text:
                bot.send_message(user_id_bc, broadcast_text, parse_mode='Markdown')
            elif photo_id:
                bot.send_photo(user_id_bc, photo_id, caption=caption, parse_mode='Markdown' if caption else None)
            elif video_id:
                bot.send_video(user_id_bc, video_id, caption=caption, parse_mode='Markdown' if caption else None)
            sent_count += 1
        except telebot.apihelper.ApiTelegramException as e:
            err_desc = str(e).lower()
            if any(s in err_desc for s in ["bot was blocked", "user is deactivated", "chat not found", "kicked from", "restricted"]):
                logger.warning(f"Broadcast failed to {user_id_bc}: User blocked/inactive.")
                blocked_count += 1
            elif "flood control" in err_desc or "too many requests" in err_desc:
                retry_after = 5; match = re.search(r"retry after (\d+)", err_desc)
                if match: retry_after = int(match.group(1)) + 1
                logger.warning(f"Flood control. Sleeping {retry_after}s...")
                time.sleep(retry_after)
                try:
                    if broadcast_text: bot.send_message(user_id_bc, broadcast_text, parse_mode='Markdown')
                    elif photo_id: bot.send_photo(user_id_bc, photo_id, caption=caption, parse_mode='Markdown' if caption else None)
                    elif video_id: bot.send_video(user_id_bc, video_id, caption=caption, parse_mode='Markdown' if caption else None)
                    sent_count += 1
                except Exception as e_retry: logger.error(f"Broadcast retry failed to {user_id_bc}: {e_retry}"); failed_count +=1
            else: logger.error(f"Broadcast failed to {user_id_bc}: {e}"); failed_count += 1
        except Exception as e: logger.error(f"Unexpected error broadcasting to {user_id_bc}: {e}"); failed_count += 1

        if (i + 1) % batch_size == 0 and i < total_users - 1:
            logger.info(f"Broadcast batch {i//batch_size + 1} sent. Sleeping {delay_batches}s...")
            time.sleep(delay_batches)
        elif i % 5 == 0: time.sleep(0.2)

    duration = round(time.time() - start_exec_time, 2)
    result_msg = (f"📢 **Broadcast Complete!**\n\n"
                  f"✅ Sent: {sent_count}\n"
                  f"❌ Failed: {failed_count}\n"
                  f"🚫 Blocked/Inactive: {blocked_count}\n"
                  f"👥 Targets: {total_users}\n"
                  f"⏱ Duration: {duration}s")
    logger.info(result_msg)
    try: bot.send_message(admin_chat_id, result_msg, parse_mode='Markdown')
    except Exception as e: logger.error(f"Failed to send broadcast result to admin {admin_chat_id}: {e}")

def admin_panel_callback(call):
    bot.answer_callback_query(call.id)
    try:
        bot.edit_message_text("👑 **Admin Panel**\nManage admins & settings.",
                              call.message.chat.id, call.message.message_id, reply_markup=create_admin_panel(), parse_mode='Markdown')
    except Exception as e: logger.error(f"Error showing admin panel: {e}")

def free_settings_callback(call):
    bot.answer_callback_query(call.id)
    try:
        bot.edit_message_text("⚙️ **Free User Settings**\n\nConfigure limits for free users.",
                              call.message.chat.id, call.message.message_id, 
                              reply_markup=create_free_settings_panel(), parse_mode='Markdown')
    except Exception as e: logger.error(f"Error showing free settings: {e}")

def toggle_free_user_callback(call):
    value = call.data.replace('toggle_free_', '')
    enabled = value.lower() == 'true'
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute('UPDATE free_user_settings SET setting_value = ? WHERE setting_key = ?', 
                  ('True' if enabled else 'False', 'enabled'))
        conn.commit()
        conn.close()
    bot.answer_callback_query(call.id, f"✅ Free users {'enabled' if enabled else 'disabled'}.")
    free_settings_callback(call)

def set_free_files_callback(call):
    bot.answer_callback_query(call.id)
    msg = bot.send_message(call.message.chat.id, "📁 Enter new file limit for free users:\n/cancel to abort.")
    bot.register_next_step_handler(msg, process_set_free_files)

def process_set_free_files(message):
    if message.from_user.id not in admin_ids:
        bot.reply_to(message, "👑 Admin only.")
        return
    if message.text.lower() == '/cancel':
        bot.reply_to(message, "❌ Cancelled.")
        free_settings_callback(message)
        return
    try:
        limit = int(message.text.strip())
        if limit < 0:
            raise ValueError("Limit must be positive")
        with DB_LOCK:
            conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
            c = conn.cursor()
            c.execute('UPDATE free_user_settings SET setting_value = ? WHERE setting_key = ?', 
                      (str(limit), 'file_limit'))
            conn.commit()
            conn.close()
        bot.reply_to(message, f"✅ Free user file limit set to: {limit}")
        free_settings_callback(message)
    except ValueError:
        bot.reply_to(message, "❌ Invalid limit. Enter a number.")
        set_free_files_callback(message)

def set_free_hours_callback(call):
    bot.answer_callback_query(call.id)
    msg = bot.send_message(call.message.chat.id, "⏰ Enter new hosting hours for free users:\n/cancel to abort.")
    bot.register_next_step_handler(msg, process_set_free_hours)

def process_set_free_hours(message):
    if message.from_user.id not in admin_ids:
        bot.reply_to(message, "👑 Admin only.")
        return
    if message.text.lower() == '/cancel':
        bot.reply_to(message, "❌ Cancelled.")
        free_settings_callback(message)
        return
    try:
        hours = int(message.text.strip())
        if hours < 0:
            raise ValueError("Hours must be positive")
        with DB_LOCK:
            conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
            c = conn.cursor()
            c.execute('UPDATE free_user_settings SET setting_value = ? WHERE setting_key = ?', 
                      (str(hours), 'hosting_hours'))
            conn.commit()
            conn.close()
        bot.reply_to(message, f"✅ Free user hosting hours set to: {hours}h")
        free_settings_callback(message)
    except ValueError:
        bot.reply_to(message, "❌ Invalid hours. Enter a number.")
        set_free_hours_callback(message)

def global_history_callback(call):
    _logic_global_history(call.message)

def add_admin_init_callback(call):
    bot.answer_callback_query(call.id)
    msg = bot.send_message(call.message.chat.id, "👤 Enter User ID to promote to Admin.\n/cancel to abort.")
    bot.register_next_step_handler(msg, process_add_admin_id)

def process_add_admin_id(message):
    owner_id_check = message.from_user.id
    if owner_id_check != OWNER_ID: bot.reply_to(message, "👑 Owner only."); return
    if message.text.lower() == '/cancel': bot.reply_to(message, "❌ Admin promotion cancelled."); return
    try:
        new_admin_id = int(message.text.strip())
        if new_admin_id <= 0: raise ValueError("ID must be positive")
        if new_admin_id == OWNER_ID: bot.reply_to(message, "👑 Owner is already Owner."); return
        if new_admin_id in admin_ids: bot.reply_to(message, f"👤 User `{new_admin_id}` already Admin."); return
        add_admin_db(new_admin_id)
        logger.warning(f"Admin {new_admin_id} added by Owner {owner_id_check}.")
        bot.reply_to(message, f"✅ User `{new_admin_id}` promoted to Admin.")
        try: bot.send_message(new_admin_id, "👑 Congrats! You are now an Admin.")
        except Exception as e: logger.error(f"Failed to notify new admin {new_admin_id}: {e}")
    except ValueError:
        bot.reply_to(message, "❌ Invalid ID. Send numerical ID or /cancel.")
        msg = bot.send_message(message.chat.id, "👤 Enter User ID to promote or /cancel.")
        bot.register_next_step_handler(msg, process_add_admin_id)
    except Exception as e: logger.error(f"Error processing add admin: {e}", exc_info=True); bot.reply_to(message, "❌ Error.")

def remove_admin_init_callback(call):
    bot.answer_callback_query(call.id)
    msg = bot.send_message(call.message.chat.id, "👤 Enter User ID of Admin to remove.\n/cancel to abort.")
    bot.register_next_step_handler(msg, process_remove_admin_id)

def process_remove_admin_id(message):
    owner_id_check = message.from_user.id
    if owner_id_check != OWNER_ID: bot.reply_to(message, "👑 Owner only."); return
    if message.text.lower() == '/cancel': bot.reply_to(message, "❌ Admin removal cancelled."); return
    try:
        admin_id_remove = int(message.text.strip())
        if admin_id_remove <= 0: raise ValueError("ID must be positive")
        if admin_id_remove == OWNER_ID: bot.reply_to(message, "👑 Owner cannot remove self."); return
        if admin_id_remove not in admin_ids: bot.reply_to(message, f"👤 User `{admin_id_remove}` not Admin."); return
        if remove_admin_db(admin_id_remove):
            logger.warning(f"Admin {admin_id_remove} removed by Owner {owner_id_check}.")
            bot.reply_to(message, f"✅ Admin `{admin_id_remove}` removed.")
            try: bot.send_message(admin_id_remove, "👑 You are no longer an Admin.")
            except Exception as e: logger.error(f"Failed to notify removed admin {admin_id_remove}: {e}")
        else: bot.reply_to(message, f"❌ Failed to remove admin `{admin_id_remove}`. Check logs.")
    except ValueError:
        bot.reply_to(message, "❌ Invalid ID. Send numerical ID or /cancel.")
        msg = bot.send_message(message.chat.id, "👤 Enter Admin ID to remove or /cancel.")
        bot.register_next_step_handler(msg, process_remove_admin_id)
    except Exception as e: logger.error(f"Error processing remove admin: {e}", exc_info=True); bot.reply_to(message, "❌ Error.")

def list_admins_callback(call):
    bot.answer_callback_query(call.id)
    try:
        admin_list_str = "\n".join(f"- `{aid}` {'👑' if aid == OWNER_ID else ''}" for aid in sorted(list(admin_ids)))
        if not admin_list_str: admin_list_str = "(No Owner/Admins configured!)"
        bot.edit_message_text(f"👑 **Current Admins:**\n\n{admin_list_str}", call.message.chat.id,
                              call.message.message_id, reply_markup=create_admin_panel(), parse_mode='Markdown')
    except Exception as e: logger.error(f"Error listing admins: {e}")

def add_subscription_init_callback(call):
    bot.answer_callback_query(call.id)
    msg = bot.send_message(call.message.chat.id, "📝 Enter User ID & days (e.g., `12345678 30`).\n/cancel to abort.")
    bot.register_next_step_handler(msg, process_add_subscription_details)

def process_add_subscription_details(message):
    admin_id_check = message.from_user.id
    if admin_id_check not in admin_ids: bot.reply_to(message, "👑 Not authorized."); return
    if message.text.lower() == '/cancel': bot.reply_to(message, "❌ Sub add cancelled."); return
    try:
        parts = message.text.split();
        if len(parts) != 2: raise ValueError("Incorrect format")
        sub_user_id = int(parts[0].strip()); days = int(parts[1].strip())
        if sub_user_id <= 0 or days <= 0: raise ValueError("User ID/days must be positive")

        current_expiry = user_subscriptions.get(sub_user_id, {}).get('expiry')
        start_date_new_sub = datetime.now()
        if current_expiry and current_expiry > start_date_new_sub: start_date_new_sub = current_expiry
        new_expiry = start_date_new_sub + timedelta(days=days)
        save_subscription(sub_user_id, new_expiry)

        logger.info(f"Sub for {sub_user_id} by admin {admin_id_check}. Expiry: {new_expiry:%Y-%m-%d}")
        bot.reply_to(message, f"✅ Sub for `{sub_user_id}` by {days} days.\n📅 New expiry: {new_expiry:%Y-%m-%d}")
        try: bot.send_message(sub_user_id, f"✅ Sub activated/extended by {days} days! Expires: {new_expiry:%Y-%m-%d}.")
        except Exception as e: logger.error(f"Failed to notify {sub_user_id} of new sub: {e}")
    except ValueError as e:
        bot.reply_to(message, f"❌ Invalid: {e}. Format: `ID days` or /cancel.")
        msg = bot.send_message(message.chat.id, "📝 Enter User ID & days, or /cancel.")
        bot.register_next_step_handler(msg, process_add_subscription_details)
    except Exception as e: logger.error(f"Error processing add sub: {e}", exc_info=True); bot.reply_to(message, "❌ Error.")

def remove_subscription_init_callback(call):
    bot.answer_callback_query(call.id)
    msg = bot.send_message(call.message.chat.id, "📝 Enter User ID to remove sub.\n/cancel to abort.")
    bot.register_next_step_handler(msg, process_remove_subscription_id)

def process_remove_subscription_id(message):
    admin_id_check = message.from_user.id
    if admin_id_check not in admin_ids: bot.reply_to(message, "👑 Not authorized."); return
    if message.text.lower() == '/cancel': bot.reply_to(message, "❌ Sub removal cancelled."); return
    try:
        sub_user_id_remove = int(message.text.strip())
        if sub_user_id_remove <= 0: raise ValueError("ID must be positive")
        if sub_user_id_remove not in user_subscriptions:
            bot.reply_to(message, f"ℹ️ User `{sub_user_id_remove}` no active sub in memory."); return
        remove_subscription_db(sub_user_id_remove)
        logger.warning(f"Sub removed for {sub_user_id_remove} by admin {admin_id_check}.")
        bot.reply_to(message, f"✅ Sub for `{sub_user_id_remove}` removed.")
        try: bot.send_message(sub_user_id_remove, "❌ Your subscription removed by admin.")
        except Exception as e: logger.error(f"Failed to notify {sub_user_id_remove} of sub removal: {e}")
    except ValueError:
        bot.reply_to(message, "❌ Invalid ID. Send numerical ID or /cancel.")
        msg = bot.send_message(message.chat.id, "📝 Enter User ID to remove sub from, or /cancel.")
        bot.register_next_step_handler(msg, process_remove_subscription_id)
    except Exception as e: logger.error(f"Error processing remove sub: {e}", exc_info=True); bot.reply_to(message, "❌ Error.")

def check_subscription_init_callback(call):
    bot.answer_callback_query(call.id)
    msg = bot.send_message(call.message.chat.id, "🔍 Enter User ID to check sub.\n/cancel to abort.")
    bot.register_next_step_handler(msg, process_check_subscription_id)

def process_check_subscription_id(message):
    admin_id_check = message.from_user.id
    if admin_id_check not in admin_ids: bot.reply_to(message, "👑 Not authorized."); return
    if message.text.lower() == '/cancel': bot.reply_to(message, "❌ Sub check cancelled."); return
    try:
        sub_user_id_check = int(message.text.strip())
        if sub_user_id_check <= 0: raise ValueError("ID must be positive")
        if sub_user_id_check in user_subscriptions:
            expiry_dt = user_subscriptions[sub_user_id_check].get('expiry')
            if expiry_dt:
                if expiry_dt > datetime.now():
                    days_left = (expiry_dt - datetime.now()).days
                    bot.reply_to(message, f"✅ User `{sub_user_id_check}` active sub.\n📅 Expires: {expiry_dt:%Y-%m-%d %H:%M:%S} ({days_left} days left).")
                else:
                    bot.reply_to(message, f"❌ User `{sub_user_id_check}` expired sub (On: {expiry_dt:%Y-%m-%d %H:%M:%S}).")
                    remove_subscription_db(sub_user_id_check)
            else: bot.reply_to(message, f"⚠️ User `{sub_user_id_check}` in sub list, but expiry missing. Re-add if needed.")
        else: bot.reply_to(message, f"ℹ️ User `{sub_user_id_check}` no active sub record.")
    except ValueError:
        bot.reply_to(message, "❌ Invalid ID. Send numerical ID or /cancel.")
        msg = bot.send_message(message.chat.id, "🔍 Enter User ID to check, or /cancel.")
        bot.register_next_step_handler(msg, process_check_subscription_id)
    except Exception as e: logger.error(f"Error processing check sub: {e}", exc_info=True); bot.reply_to(message, "❌ Error.")

# =============== DATABASE FUNCTIONS ===============

def add_hosting(user_id, time_str, files):
    if time_str.endswith('h'):
        hours = int(time_str[:-1])
        expiry = datetime.now() + timedelta(hours=hours)
    elif time_str.endswith('d'):
        days = int(time_str[:-1])
        expiry = datetime.now() + timedelta(days=days)
    else:
        return False
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            c.execute('INSERT OR REPLACE INTO user_hosting (user_id, hosting_time, file_count) VALUES (?, ?, ?)',
                      (user_id, expiry.isoformat(), files))
            conn.commit()
            user_hosting[user_id] = {'hosting_time': expiry, 'file_count': files}
            logger.info(f"Added hosting for {user_id} until {expiry.isoformat()} with {files} files")
        except Exception as e: logger.error(f"Error adding hosting: {e}")
        finally: conn.close()
    return True

def remove_hosting(user_id):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            c.execute('DELETE FROM user_hosting WHERE user_id = ?', (user_id,))
            conn.commit()
            if user_id in user_hosting: del user_hosting[user_id]
            logger.info(f"Removed hosting for {user_id}")
        except Exception as e: logger.error(f"Error removing hosting: {e}")
        finally: conn.close()

def add_prime(user_id, time_str, files):
    if time_str.endswith('h'):
        hours = int(time_str[:-1])
        expiry = datetime.now() + timedelta(hours=hours)
    elif time_str.endswith('d'):
        days = int(time_str[:-1])
        expiry = datetime.now() + timedelta(days=days)
    else:
        return False
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            c.execute('INSERT OR REPLACE INTO user_prime (user_id, prime_time) VALUES (?, ?)',
                      (user_id, expiry.isoformat()))
            conn.commit()
            user_prime[user_id] = {'prime_time': expiry}
            logger.info(f"Added prime for {user_id} until {expiry.isoformat()}")
        except Exception as e: logger.error(f"Error adding prime: {e}")
        finally: conn.close()
    return True

def add_vip(user_id, time_str, files):
    if time_str.endswith('d'):
        days = int(time_str[:-1])
        expiry = datetime.now() + timedelta(days=days)
    elif time_str.endswith('h'):
        hours = int(time_str[:-1])
        expiry = datetime.now() + timedelta(hours=hours)
    else:
        return False
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            c.execute('INSERT OR REPLACE INTO user_vip (user_id, vip_time) VALUES (?, ?)',
                      (user_id, expiry.isoformat()))
            conn.commit()
            user_vip[user_id] = {'vip_time': expiry}
            logger.info(f"Added vip for {user_id} until {expiry.isoformat()}")
        except Exception as e: logger.error(f"Error adding vip: {e}")
        finally: conn.close()
    return True

def add_ban(user_id):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            c.execute('INSERT OR IGNORE INTO user_ban (user_id) VALUES (?)', (user_id,))
            conn.commit()
            user_ban.add(user_id)
            logger.info(f"Banned user {user_id}")
        except Exception as e: logger.error(f"Error banning user: {e}")
        finally: conn.close()

def remove_ban(user_id):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            c.execute('DELETE FROM user_ban WHERE user_id = ?', (user_id,))
            conn.commit()
            user_ban.discard(user_id)
            logger.info(f"Unbanned user {user_id}")
        except Exception as e: logger.error(f"Error unbanning user: {e}")
        finally: conn.close()

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

if __name__ == '__main__':
    logger.info("="*40 + "\n🌟 BRONX ULTRA OSINT BOT v21.0 🌟\n" + 
                f"🐍 Python: {sys.version.split()[0]}\n" +
                f"📁 Base Dir: {BASE_DIR}\n" +
                f"📂 Upload Dir: {UPLOAD_BOTS_DIR}\n" +
                f"💾 Data Dir: {IROTECH_DIR}\n" +
                f"👑 Owner ID: {OWNER_ID}\n" +
                f"👨‍💼 Admins: {admin_ids}\n" +
                f"⚡ Response Time: 10ms (Flash of Light)\n" +
                f"💾 RAM: 500GB\n" +
                f"📁 Storage: Unlimited\n" +
                f"⏱ Start Time: {BOT_START_TIME}" + "="*40)
    keep_alive()
    scheduler_thread = threading.Thread(target=schedule_check, daemon=True)
    scheduler_thread.start()
    logger.info("🚀 Starting polling...")
    while True:
        try:
            bot.infinity_polling(logger_level=logging.INFO, timeout=60, long_polling_timeout=30)
        except requests.exceptions.ReadTimeout: logger.warning("⏱ Polling ReadTimeout. Restarting in 5s..."); time.sleep(5)
        except requests.exceptions.ConnectionError as ce: logger.error(f"🔌 Polling ConnectionError: {ce}. Retrying in 15s..."); time.sleep(15)
        except Exception as e:
            logger.critical(f"💥 Unrecoverable polling error: {e}", exc_info=True)
            logger.info("🔄 Restarting polling in 30s due to critical error..."); time.sleep(30)
        finally: logger.warning("🔄 Polling attempt finished. Will restart if in loop."); time.sleep(1)
