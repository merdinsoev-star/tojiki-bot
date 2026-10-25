import os, json, requests
from datetime import datetime, timezone
import pytz
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.environ.get("BOT_TOKEN")
REVIEW_CHANNEL = os.environ.get("REVIEW_CHANNEL")
SIGNAL_CHANNEL = os.environ.get("SIGNAL_CHANNEL")

ACTIVE_FILE = "active_trades.json"
DUSHANBE_TZ = pytz.timezone('Asia/Dushanbe')

def load_active():
    try:
        with open(ACTIVE_FILE, 'r') as f: return json.load(f)
    except: return {}
def save_active(d):
    with open(ACTIVE_FILE, 'w') as f: json.dump(d, f)

# === 0. САНҶИШИ БОЗОР МАҲКАМ Ё КУШОДА ===
def is_market_closed():
    now_utc = datetime.now(timezone.utc)
    weekday = now_utc.weekday() # 0=Душанбе 6=Якшанбе
    
    # FOREX/XAUUSD: Шанбе 22:00 UTC то Душанбе 22:00 UTC маҳкам
    # Ҷумъа шаб маҳкам мешавад, Душанбе шаб кушода
    if weekday == 5: # Шанбе
        return True, "Шанбе"
    if weekday == 6: # Якшанбе
        return True, "Якшанбе"
    if weekday == 4 and now_utc.hour >= 21: # Ҷумъа 21:00 UTC = 02:00 Душанбе
        return True, "Ҷумъа шаб"
    
    return False, "Кушода"

# === 1. НАРХИ ДУРУСТ АЗ 3 СЕРВЕР ===
def get_price(symbol):
    yahoo = "GC=F" if symbol=="XAUUSD" else "EURUSD=X"
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{yahoo}?interval=1m&range=1d"
        r = requests.get(url, headers={'User-Agent':'Mozilla/5.0'}, timeout=8).json()
        price = r['chart']['result'][0]['meta']['regularMarketPrice']
        return float(price), "Yahoo Finance 🌍"
    except:
        try:
            if symbol=="XAUUSD":
                # GoldAPI backup
                price = requests.get("https://api.metals.live/v1/spot", timeout=5).json()[0]['gold']
            else:
                price = requests.get("https://api.exchangerate.host/latest?base=EUR&symbols=USD", timeout=5).json()['rates']['USD']
            return float(price), "Backup Server"
        except:
            return None, "Error"

def get_candles_full(symbol):
    yahoo = "GC=F" if symbol=="XAUUSD" else "EURUSD=X"
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{yahoo}?interval=15m&range=5d"
        r = requests.get(url, headers={'User-Agent':'Mozilla/5.0'}, timeout=10).json()
        res = r['chart']['result'][0]
        closes = res['indicators']['quote'][0]['close']
        highs = res['indicators']['quote'][0]['high']
        lows = res['indicators']['quote'][0]['low']
        volumes = res['indicators']['quote'][0].get('volume', [1000]*len(closes))
        
        # Тоза кардан
        data = []
        for i in range(len(closes)):
            if closes[i] and highs[i] and lows[i]:
                data.append({
                    'c': closes[i], 'h': highs[i], 'l': lows[i],
                    'v': volumes[i] if volumes and volumes[i] else 1000
                })
        return data[-100:] # 100 шамъи
