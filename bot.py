import os, json, requests
from datetime import datetime, timezone
import pytz
from flask import Flask, request
import threading
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

flask_app = Flask(__name__)

TOKEN = os.environ.get("BOT_TOKEN")
REVIEW_CHANNEL = os.environ.get("REVIEW_CHANNEL")
SIGNAL_CHANNEL = os.environ.get("SIGNAL_CHANNEL")
ACTIVE_FILE = "active_trades.json"
DUSHANBE_TZ = pytz.timezone('Asia/Dushanbe')

def load_active():
    try:
        with open(ACTIVE_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_active(d):
    with open(ACTIVE_FILE, 'w') as f:
        json.dump(d, f)

def is_market_closed():
    now_utc = datetime.now(timezone.utc)
    w = now_utc.weekday()
    if w == 5:
        return True, "Shanbe"
    if w == 6:
        return True, "Yakshanbe"
    if w == 4 and now_utc.hour >= 21:
        return True, "Juma shab"
    return False, "Kushoda"

def get_price(symbol):
   
