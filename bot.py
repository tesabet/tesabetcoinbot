from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler
import random

# Bot tokeni
BOT_TOKEN = "AAHclqnExmf1FsIlptHPalXnEC5zlxFHMTY"

# Kullanıcı verileri
users = {}
eth_payments = {}  # chat_id: ödenen ETH miktarı

# Başlangıç coin ve seviye
START_COIN = 10
START_LEVEL = 1

# Görev zorluk ayarları
def get_task_reward(level):
    base_coin = max(5, 20 - level*2)  # seviye arttıkça coin azalır
    eth_bonus = base_coin * 2  # ETH ile tamamlayınca ekstra coin
    return base_coin, eth_bonus

# Slot ödülleri seviyeye göre
def get_slot_reward(level, jackpot=False):
    base = max(10, 50 - level*3)
    if jackpot:
        return base * 2
    return base

# Oyun başlat
def game_start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    if chat_id not in users:
        users[chat_id] = {"coin": START_COIN, "level": START_LEVEL}
    show_game_menu(chat_id, update, context)

# Oyun menüsü
def show_game_menu(chat_id, update, context):
    keyboard = [
        [InlineKeyboardButton("Görevler 📝", callback_data='tasks')],
        [InlineKeyboardButton("Slot Oyna 🎰", callback_data='slot')],
        [InlineKeyboardButton("Profil 👤", callback_data='profil')],
        [InlineKeyboardButton("Market 🏪", callback_data='market')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(chat_id=chat_id, text="🎮 Oyun ekranına hoş geldin! Görevlerini seçebilirsin.", reply_markup=reply_markup)

# Menü butonları
def button(update: Update, context: CallbackContext):
    query = update.callback_query
    chat_id = query.message.chat_id
    query.answer()
    if chat_id not in users:
        users[chat_id] = {"coin": START_COIN, "level": START_LEVEL}
    data = query.data
    level = users[chat_id]["level"]

    # Görevler menüsü
    if data == "tasks":
        keyboard = [
            [InlineKeyboardButton("Mini Test 📝", callback_data='task_test')],
            [InlineKeyboardButton("Günlük Bonus 💰", callback_data='task_bonus')],
            [InlineKeyboardButton("Arkadaş Davet Et 👥", callback_data='task_invite')],
            [InlineKeyboardButton("ETH ile Görev Tamamla 💎", callback_data='task_eth')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text("📜 Görevlerini seç:", reply_markup=reply_markup)

    # Görev işlemleri
    elif data.startswith("task_"):
        base_coin, eth_bonus = get_task_reward(level)
        if data == "task_test":
            users[chat_id]["coin"] += base_coin
            query.edit_message_text(f"✅ Mini testi tamamladın! {base_coin} coin kazandın 🎉")
        elif data == "task_bonus":
            users[chat_id]["coin"] += base_coin
            query.edit_message_text(f"💰 Günlük bonusunu aldın! {base_coin} coin kazandın 🎉")
        elif data == "task_invite":
            users[chat_id]["coin"] += base_coin
            query.edit_message_text(f"👥 Arkadaş davetini tamamladın! {base_coin} coin kazandın 🎉")
        elif data == "task_eth":
            eth_amount = 0.001  # Ödeme miktarı örnek
            eth_payments[chat_id] = eth_amount
            users[chat_id]["coin"] += eth_bonus
            users[chat_id]["level"] += 1
            query.edit_message_text(f"💎 ETH ile görev tamamlandı! {eth_bonus} coin ve 1 seviye kazandın 🎉")
        show_game_menu(chat_id, update, context)

    # Slot
    elif data == "slot":
        emojis = ["🍒", "🍋", "🍉", "⭐", "7️⃣"]
        result = [random.choice(emojis) for _ in range(3)]
        message = " | ".join(result)
        if len(set(result)) == 1:
            win = get_slot_reward(level, jackpot=True)
            users[chat_id]["coin"] += win
            query.edit_message_text(f"🎰 {message}\nJackpot! {win} coin kazandın 🎉")
        elif len(set(result)) == 2:
            win = get_slot_reward(level, jackpot=False)
            users[chat_id]["coin"] += win
            query.edit_message_text(f"🎰 {message}\nTebrikler! {win} coin kazandın 🎉")
        else:
            query.edit_message_text(f"🎰 {message}\nKaybettin 😢")
        show_game_menu(chat_id, update, context)

    # Profil
    elif data == "profil":
        coin = users[chat_id]["coin"]
        level = users[chat_id]["level"]
        query.edit_message_text(f"👤 Profilin:\nSeviye: {level}\nCoin: {coin}")
        show_game_menu(chat_id, update, context)

    # Market
    elif data == "market":
        query.edit_message_text("🏪 Market:\n- 100 coin = Güçlü Kılıç ⚔️\n- 50 coin = Can iksiri ❤️")
        show_game_menu(chat_id, update, context)

# Telegram komutu /start
def start(update: Update, context: CallbackContext):
    keyboard = [[InlineKeyboardButton("Start ▶️", callback_data='start_game')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("🌟 Rise of Tesabet’e Hoş Geldin! Tek tuşla oyuna başla.", reply_markup=reply_markup)

# Start butonu callback
def start_game_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    game_start(update, context)

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(start_game_callback, pattern="start_game"))
    dp.add_handler(CallbackQueryHandler(button))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()