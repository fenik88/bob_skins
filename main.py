from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ConversationHandler, filters, ContextTypes
)
import uuid

# --- States ---
MAIN, BUY_SKINS, STEAM_LINK, CONFIRM_ORDER, TOP_UP, EXCHANGE, EXCHANGE_TYPE, WALLET, AMOUNT, SCREENSHOT, CURRENCY, CONFIRM_EXCHANGE = range(12)

ADMIN_CHAT_ID = 778268974  # numeric chat ID, not @username

# --- Start / Main Menu ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Buy Skins", callback_data='buy_skins')],
        [InlineKeyboardButton("Top Up Trading Platform", callback_data='top_up')],
        [InlineKeyboardButton("Exchange Yuan", callback_data='exchange')]
    ]
    if update.message:
        await update.message.reply_text(
            "Welcome! Choose your type of order:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    elif update.callback_query:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(
            "Welcome! Choose your type of order:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    return MAIN


async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("Buy Skins", callback_data='buy_skins')],
        [InlineKeyboardButton("Top Up Trading Platform", callback_data='top_up')],
        [InlineKeyboardButton("Exchange Yuan", callback_data='exchange')]
    ]
    await query.edit_message_text(
        "Welcome! Choose your type of order:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return MAIN


# --- Variant 1: Buy Skins ---
async def buy_skins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [[InlineKeyboardButton("Back to Main Menu", callback_data='main')]]
    await query.edit_message_text(
        "Okay, now provide us with a valid Steam link/links to the collectible(s).",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return STEAM_LINK


async def handle_steam_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['steam_link'] = update.message.text
    keyboard = [
        [InlineKeyboardButton("Send Order", callback_data='send_order')],
        [InlineKeyboardButton("Back", callback_data='buy_skins')]
    ]
    await update.message.reply_text(
        f"Okay, received your link: {update.message.text}\nWhat do you want to do?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return CONFIRM_ORDER


async def send_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    order_id = str(uuid.uuid4())[:8]

    message_to_admin = (
        f"📦 New Order Received\n"
        f"Order ID: {order_id}\n"
        f"From: @{user.username or user.id}\n"
        f"Type: Buy Skins\n"
        f"Steam Link: {context.user_data.get('steam_link', 'N/A')}"
    )

    await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=message_to_admin)

    keyboard = [
        [InlineKeyboardButton("Create Another Order", callback_data='buy_skins')],
        [InlineKeyboardButton("Back to Main Menu", callback_data='main')]
    ]
    await query.edit_message_text(
        "Order was sent. Support will get back to you soon!",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return MAIN


# --- Variant 2: Top Up Trading Platform ---
async def top_up(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [[InlineKeyboardButton("Back to Main Menu", callback_data='main')]]
    await query.edit_message_text(
        "This feature is in development.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return MAIN


# --- Variant 3: Exchange Yuan ---
async def exchange(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("Buy Yuan", callback_data='buy_yuan')],
        [InlineKeyboardButton("Sell Yuan", callback_data='sell_yuan')],
        [InlineKeyboardButton("Back", callback_data='main')]
    ]
    await query.edit_message_text(
        "What do you want to do?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return EXCHANGE_TYPE


async def wallet_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    action = query.data

    if action == 'sell_yuan':
        keyboard = [[InlineKeyboardButton("Back", callback_data='exchange')]]
        await query.edit_message_text(
            "This feature is in development.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return EXCHANGE_TYPE

    context.user_data['exchange_action'] = action
    keyboard = [
        [InlineKeyboardButton("Alipay", callback_data='alipay')],
        [InlineKeyboardButton("WeChat Pay", callback_data='wechat')],
        [InlineKeyboardButton("Back", callback_data='exchange')]
    ]
    await query.edit_message_text(
        "Which wallet do you want to use?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return WALLET


async def enter_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data['wallet'] = query.data
    keyboard = [[InlineKeyboardButton("Back", callback_data='exchange')]]
    await query.edit_message_text(
        "Enter the amount in USD you want to exchange:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return AMOUNT


async def handle_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['amount'] = update.message.text
    keyboard = [[InlineKeyboardButton("Back", callback_data='exchange')]]
    await update.message.reply_text(
        "Please send a screenshot of your deposit QR code.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return SCREENSHOT


async def handle_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    context.user_data['screenshot_file_id'] = photo.file_id
    keyboard = [
        [InlineKeyboardButton("USDT", callback_data='usdt')],
        [InlineKeyboardButton("USDC", callback_data='usdc')],
        [InlineKeyboardButton("Back", callback_data='exchange')]
    ]
    await update.message.reply_text(
        "Choose the currency you want to pay with:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return CURRENCY


async def confirm_exchange(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data['currency'] = query.data
    keyboard = [
        [InlineKeyboardButton("Send Order", callback_data='send_exchange_order')],
        [InlineKeyboardButton("Cancel Order", callback_data='main')]
    ]
    await query.edit_message_text(
        "Confirm to send your order or cancel it.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return CONFIRM_EXCHANGE


async def send_exchange_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    order_id = str(uuid.uuid4())[:8]

    message_to_admin = (
        f"💱 New Exchange Order\n"
        f"Order ID: {order_id}\n"
        f"From: @{user.username or user.id}\n"
        f"Action: {context.user_data.get('exchange_action', 'N/A')}\n"
        f"Wallet: {context.user_data.get('wallet', 'N/A')}\n"
        f"Amount: {context.user_data.get('amount', 'N/A')}\n"
        f"Currency: {context.user_data.get('currency', 'N/A')}"
    )

    if 'screenshot_file_id' in context.user_data:
        await context.bot.send_photo(
            chat_id=ADMIN_CHAT_ID,
            photo=context.user_data['screenshot_file_id'],
            caption=message_to_admin
        )
    else:
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=message_to_admin)

    keyboard = [
        [InlineKeyboardButton("Create New Order", callback_data='exchange')],
        [InlineKeyboardButton("Back to Main Menu", callback_data='main')]
    ]
    await query.edit_message_text(
        "Success! Your order has been created.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return MAIN


# --- Handler setup ---
def main():
    application = Application.builder().token("YOUR_BOT_TOKEN_HERE").build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            MAIN: [
                CallbackQueryHandler(buy_skins, pattern='^buy_skins$'),
                CallbackQueryHandler(top_up, pattern='^top_up$'),
                CallbackQueryHandler(exchange, pattern='^exchange$')
            ],
            STEAM_LINK: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_steam_link),
                CallbackQueryHandler(main_menu, pattern='^main$')
            ],
            CONFIRM_ORDER: [
                CallbackQueryHandler(send_order, pattern='^send_order$'),
                CallbackQueryHandler(buy_skins, pattern='^buy_skins$')
            ],
            EXCHANGE_TYPE: [
                CallbackQueryHandler(wallet_selection, pattern='^(buy_yuan|sell_yuan)$'),
                CallbackQueryHandler(main_menu, pattern='^main$')
            ],
            WALLET: [
                CallbackQueryHandler(enter_amount, pattern='^(alipay|wechat)$'),
                CallbackQueryHandler(exchange, pattern='^exchange$')
            ],
            AMOUNT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_amount),
                CallbackQueryHandler(exchange, pattern='^exchange$')
            ],
            SCREENSHOT: [
                MessageHandler(filters.PHOTO, handle_screenshot),
                CallbackQueryHandler(exchange, pattern='^exchange$')
            ],
            CURRENCY: [
                CallbackQueryHandler(confirm_exchange, pattern='^(usdt|usdc)$'),
                CallbackQueryHandler(exchange, pattern='^exchange$')
            ],
            CONFIRM_EXCHANGE: [
                CallbackQueryHandler(send_exchange_order, pattern='^send_exchange_order$'),
                CallbackQueryHandler(main_menu, pattern='^main$')
            ],
        },
        fallbacks=[CallbackQueryHandler(main_menu, pattern='^main$')],
        per_message=False  # ✅ fixed warning
    )

    application.add_handler(conv_handler)
    application.run_polling()


if __name__ == '__main__':
    main()