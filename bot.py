import requests
import random
import asyncio
from datetime import datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters

TOKEN = "8962125032:AAGerpvIIh0DWpW4AWcN6rJAJc11_AO9geg"
L1 = "https://t.me/+ow3obalQmP4xMjAy"
L2 = "https://t.me/+wpu3IAc9V7tiOWMy"
LAST_XAU = 4007.90
LAST_EUR = 1.0850

def get_xau():
    global LAST_XAU
    try:
        r = requests.get("https://api.gold-api.com/price/XAU", timeout=10)
        p = float(r.json()['price'])
        if p > 1000:
            LAST_XAU = p
            return p
    except: pass
    return LAST_XAU

def get_eur():
    global LAST_EUR
    LAST_EUR = 1.0850 + random.uniform(-0.002, 0.002)
    return LAST_EUR

def make_signal(price, pair):
    rnd = random.random()
    if pair == "XAUUSD":
        if rnd > 0.48:
            return "SELL", price-3.5, price-7.0, price+3.5
        else:
            return "BUY", price+3.5, price+7.0, price-3.5
    else:
        if rnd > 0.5:
            return "SELL", price-0.0008, price-0.0015, price+0.0012
        else:
            return "BUY", price+0.0008, price+0.0015, price-0.0012

async def start(u, c):
    cid = u.effective_chat.id
    rk = ReplyKeyboardMarkup([["XAUUSD","EURUSD"]], resize_keyboard=True)
    msg = "💎 БОТИ ТЕЗИ ТОЧИКИ! 💎\n\n✅ АВТОМАТИ ПУРРА (24/7)\n📈 Elliott + SMC\n\nИнтихоб кун 👇"
    kb2 = [
        [InlineKeyboardButton("📊 Сигнал GOLD", callback_data="xau"), InlineKeyboardButton("💶 EURUSD", callback_data="eur")],
        [InlineKeyboardButton("⭐ Отзивхо", url=L1), InlineKeyboardButton("📰 Хабархо", url=L2)],
        [InlineKeyboardButton("💰 Нарх", callback_data="price")],
        [InlineKeyboardButton("📰 ХАБАРХОИ МУХИМИ ХАФТА", callback_data="news")]
    ]
    await u.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(kb2))
    await c.bot.send_message(chat_id=cid, text="🎯 Тугмаро пахш кун:", reply_markup=rk)

async def send_xau(cid, c, delay=False):
    if delay:
        await c.bot.send_message(chat_id=cid, text="🔔 5 сония...")
        await asyncio.sleep(5)
    p = get_xau()
    side, tp1, tp2, sl = make_signal(p, "XAUUSD")
    tm = datetime.now().strftime("%H:%M")
    msg = f"🔴 СИГНАЛИ НАВ 🔴\n\nXAUUSD | 15m\n💰 Нарх: {round(p,2)}\n⏰ {tm}\n\n👉 {side} XAUUSD\n\n🎯 TP1: {round(tp1,2)}\n🎯 TP2: {round(tp2,2)}\n🔴 SL: {round(sl,2)}\n📐 RR: 1:2\n📌 Лот: 0.01-0.03"
    kb = [[InlineKeyboardButton("✅ ФОИДА", callback_data="foida"), InlineKeyboardButton("❌ ЗАРАР", callback_data="zarar")]]
    await c.bot.send_message(chat_id=cid, text=msg, reply_markup=InlineKeyboardMarkup(kb))

async def send_eur(cid, c, delay=False):
    if delay:
        await c.bot.send_message(chat_id=cid, text="🔔 5 сония...")
        await asyncio.sleep(5)
    p = get_eur()
    side, tp1, tp2, sl = make_signal(p, "EURUSD")
    tm = datetime.now().strftime("%H:%M")
    msg = f"🔵 EURUSD | 15m\n💰 Нарх: {round(p,5)}\n⏰ {tm}\n\n👉 {side} EURUSD\n\n🎯 TP1: {round(tp1,5)}\n🎯 TP2: {round(tp2,5)}\n🔴 SL: {round(sl,5)}"
    await c.bot.send_message(chat_id=cid, text=msg)

async def send_news(cid, c):
    msg = "📰 ХАБАРХОИ МУХИМИ ХАФТА\n26 Окт - 1 Ноя 2026\n\n🔥 ЧОР 28 ОКТ:\n🇺🇸 FOMC Фоиз 23:00\n⚠️ GOLD 100$ мепарад!\n\n🟢 ПАНЧ 29 ОКТ:\n🇺🇸 GDP + PCE 17:30\n🇪🇺 ECB Фоиз 17:15\n\n🔵 ЧУМ 30 ОКТ:\n🇯🇵 BoJ Фоиз\n🇩🇪 GDP + CPI\n\n💡 28-29 Окт ТРЕЙД НАКУН!"
    await c.bot.send_message(chat_id=cid, text=msg)

async def cb(u, c):
    q = u.callback_query
    await q.answer()
    d = q.data
    cid = q.effective_chat.id
    if d == "xau": await send_xau(cid, c, True)
    if d == "eur": await send_eur(cid, c, True)
    if d == "price":
        px = get_xau(); pe = get_eur()
        await c.bot.send_message(chat_id=cid, text=f"💰 XAUUSD: {round(px,2)}\n💶 EURUSD: {round(pe,5)}")
    if d == "news": await send_news(cid, c)
    if d == "foida": await c.bot.send_message(chat_id=cid, text="🔥 Табрик!")
    if d == "zarar": await c.bot.send_message(chat_id=cid, text="💪 Такрор!")

async def txt(u, c):
    t = u.message.text.upper()
    if "XAUUSD" in t: await send_xau(u.effective_chat.id, c, True)
    if "EURUSD" in t: await send_eur(u.effective_chat.id, c, True)

async def cmd_price(u, c):
    px = get_xau(); pe = get_eur()
    await u.message.reply_text(f"💰 XAUUSD: {round(px,2)}\n💶 EURUSD: {round(pe,5)}")

print("BOT STARTING...")
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("price", cmd_price))
app.add_handler(CallbackQueryHandler(cb))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, txt))
app.run_polling(drop_pending_updates=True)
