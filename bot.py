# bot.py
import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes
)
from signal_engine import get_signal
from broker import get_balance, place_trade

TOKEN = os.environ.get("TOKEN")

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⚡ NexusBot Forex LIVE!\n\n"
        "/signal EURUSD  — Get signal\n"
        "/trade  EURUSD  — Execute trade\n"
        "/balance        — Account balance"
    )

async def signal_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    raw  = ctx.args[0] if ctx.args else "EURUSD"
    pair = raw[:3]+"/"+raw[3:]
    s    = get_signal(pair)
    await update.message.reply_text(
        f"📊 {s['pair']} — {s['action']}\n"
        f"Entry: {s['entry']}\n"
        f"SL:    {s['sl']}\n"
        f"TP:    {s['tp']}\n"
        f"RSI:   {s['rsi']}\n"
        f"Conf:  {s['confidence']}%"
    )

async def trade_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    raw  = ctx.args[0] if ctx.args else "EURUSD"
    pair = raw[:3]+"/"+raw[3:]
    s    = get_signal(pair)
    if s["confidence"] < 70:
        await update.message.reply_text("⚠️ Signal too weak.")
        return
    o = place_trade(s)
    await update.message.reply_text(
        f"✅ Trade Placed\n"
        f"Order: {o['id']}\n"
        f"Price: {o['price']}\n"
        f"Status: {o['status']}"
    )

async def balance_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    b  = get_balance()
    pl = float(b["unrealized_pl"])
    await update.message.reply_text(
        f"💰 Balance\n"
        f"{b['currency']} {b['balance']}\n"
        f"P&L: {'+'if pl>=0 else ''}{b['unrealized_pl']}"
    )

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start",   start))
app.add_handler(CommandHandler("signal",  signal_cmd))
app.add_handler(CommandHandler("trade",   trade_cmd))
app.add_handler(CommandHandler("balance", balance_cmd))
print("Bot running...")
app.run_polling()
