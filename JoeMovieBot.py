from config import ADMIN_ID
import telebot
from telebot import types
from config import TOKEN
from database import init_db, save_payment, get_movie_file_info
import os
import sys
import time
from datetime import datetime

# Initialize bot with better error handling
try:
    bot = telebot.TeleBot(TOKEN)
    print(f"✅ Bot initialized at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🤖 Bot Username: @{bot.get_me().username}")
    print(f"🆔 Bot ID: {bot.get_me().id}")
except Exception as e:
    print(f"❌ Failed to initialize bot: {e}")
    sys.exit(1)

# Enhanced database initialization
try:
    init_db()
    print("💾 Database connection established and tables verified")
except Exception as e:
    print(f"❌ Database initialization failed: {e}")
    sys.exit(1)

# Add startup notification to admin
def notify_admin():
    try:
        bot.send_message(
            ADMIN_ID,
            f"🟢 Bot Started Successfully!\n"
            f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"🐍 Python {sys.version.split()[0]}\n"
            f"📦 Version: 1.0.0"  # Update this with your actual version
        )
    except Exception as e:
        print(f"⚠️ Failed to send startup notification: {e}")

# Send notification (will only work if polling starts successfully)
notify_admin()

# Function to create a payment keyboard
def payment_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    pay_button = types.InlineKeyboardButton(text="💳 Pay  XTR", pay=True)
    help_button = types.InlineKeyboardButton(text="ℹ️ Help", callback_data="show_help")
    keyboard.add(pay_button, help_button)
    return keyboard

# Function to create a start keyboard with "Request Movie" button
def start_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton(text="Request a Movie", callback_data="request_movie")
    keyboard.add(button)
    return keyboard

# /start command handler
@bot.message_handler(commands=['start'])
def handle_start(message):
    welcome_text = """
🎥 Welcome to *Cinemate*! 🍿

I can help you request movies easily. Here's how:

1. Click *"Request a Movie"* below
2. Complete the payment
3. Receive your movie link!

Type /help to see all available commands.
"""
    bot.send_message(
        message.chat.id,
        welcome_text,
        reply_markup=start_keyboard(),
        parse_mode='Markdown'
    )

@bot.callback_query_handler(func=lambda call: call.data == "show_help")
def show_help_callback(call):
    handle_help(call.message)
    bot.answer_callback_query(call.id)

@bot.message_handler(commands=['mystatus'])
def handle_mystatus(message):
    user_id = message.from_user.id
    try:
        with psycopg2.connect(DATABASE) as conn:
            with conn.cursor() as cursor:
                cursor.execute('''
                    SELECT payment_id, request_timestamp 
                    FROM payments 
                    WHERE user_id = %s
                    ORDER BY request_timestamp DESC
                    LIMIT 5
                ''', (user_id,))
                requests = cursor.fetchall()
        
        if requests:
            status_msg = "📋 Your Last 5 Requests:\n\n"
            for req in requests:
                status_msg += f"• {req[0]} - {req[1].strftime('%Y-%m-%d %H:%M')}\n"
            status_msg += "\nUse /support if you have questions."
        else:
            status_msg = "You haven't made any requests yet. Use /start to begin!"
        
        bot.send_message(message.chat.id, status_msg)
        
    except Exception as e:
        bot.reply_to(message, f"⚠️ Error checking your status: {e}")



@bot.message_handler(commands=['admin'])
def admin_check(message):
    """Verify admin status"""
    if message.from_user.id == ADMIN_ID:
        bot.reply_to(message, "✅ You are recognized as admin!")
    else:
        bot.reply_to(message, "❌ Access denied!")

@bot.message_handler(commands=['addmovie'])
@bot.message_handler(commands=['addmovie'], content_types=['text', 'document'])
def handle_add_movie(message):
    """Admin-only movie adder that accepts either text command or document"""
    if message.from_user.id != ADMIN_ID:
        return bot.reply_to(message, "❌ Admin only!")
    
    try:
        if message.document:  # If admin sent a document
            file_id = message.document.file_id
            file_name = message.document.file_name
            file_type = message.document.mime_type
            
            # Get payment_id from caption or prompt admin
            if not message.caption:
                msg = bot.reply_to(message, "Please reply with the payment ID for this movie:")
                bot.register_next_step_handler(msg, process_payment_id_step, file_id, file_name, file_type)
                return
            
            payment_id = message.caption.strip()
            process_movie_upload(payment_id, file_id, file_name, file_type, message)
            
        else:  # If admin sent text command
            try:
                _, payment_id, file_id, file_name, file_type = message.text.split(maxsplit=4)
                process_movie_upload(payment_id, file_id, file_name, file_type, message)
            except ValueError:
                bot.reply_to(message, "Usage for text:\n/addmovie <payment_id> <file_id> <file_name> <file_type>\n\nOr just send the file with payment ID as caption")
                
    except Exception as e:
        bot.reply_to(message, f"⚠️ Error: {e}")

def process_payment_id_step(message, file_id, file_name, file_type):
    """Process payment ID after admin sends document without caption"""
    try:
        payment_id = message.text.strip()
        process_movie_upload(payment_id, file_id, file_name, file_type, message)
    except Exception as e:
        bot.reply_to(message, f"⚠️ Error: {e}")

def process_movie_upload(payment_id, file_id, file_name, file_type, message):
    """Common processing for movie uploads"""
    user_id = update_movie_file(payment_id, file_id, file_name, file_type)
    if user_id:
        try:
            # Notify user
            bot.send_message(
                user_id,
                f"🎬 Your movie is ready!\n\n"
                f"📁 File: {file_name}\n"
                f"💾 Type: {file_type.split('/')[-1].upper()}\n\n"
                f"Download below 👇"
            )
            bot.send_document(user_id, file_id, caption=file_name)
            
            # Confirm to admin
            bot.reply_to(message, f"✅ Movie sent to user {user_id}")
        except Exception as e:
            bot.reply_to(message, f"⚠️ Movie saved but failed to notify user: {e}")
    else:
        bot.reply_to(message, "❌ Payment ID not found")

def admin_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton("/addmovie"))
    keyboard.add(types.KeyboardButton("/stats"))
    return keyboard

@bot.message_handler(commands=['panel'])
def admin_panel(message):
    if message.from_user.id == ADMIN_ID:
        bot.send_message(
            message.chat.id,
            "Admin panel:",
            reply_markup=admin_keyboard()
            )       

@bot.message_handler(commands=['help'])
def handle_help(message):
    help_text = """
🎬 *Cinemate Bot Commands* 🎬

*Main Commands:*
/start - Start interacting with the bot
/help - Show this help message
/support - Contact support

*Movie Commands:*
/request - Request a movie (also available via button)
/mystatus - Check your pending requests

*Admin Commands* (Admin only):
/addmovie - Add a movie to a payment
/stats - View bot statistics
/panel - Admin control panel

Click buttons or type commands to interact with me!
"""
    bot.send_message(message.chat.id, help_text, parse_mode='Markdown')

# "Request Movie" button handler
@bot.callback_query_handler(func=lambda call: call.data == "request_movie")
def handle_request_movie(call):
    prices = [types.LabeledPrice(label="XTR", amount=500)]  # 500 XTR
    bot.send_invoice(
        call.message.chat.id,
        title="Movie Request",
        description="Request a movie for 1 XTR!",
        invoice_payload="movie_request_payload",
        provider_token="",  # Add your payment provider token here
        currency="XTR",
        prices=prices,
        reply_markup=payment_keyboard()
    )

# Pre-checkout handler
@bot.pre_checkout_query_handler(func=lambda query: True)
def handle_pre_checkout_query(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

# Successful payment handler
@bot.message_handler(content_types=['successful_payment'])
def handle_successful_payment(message):
    user_id = message.from_user.id
    payment_id = message.successful_payment.provider_payment_charge_id
    amount = message.successful_payment.total_amount
    currency = message.successful_payment.currency

    # Send payment confirmation
    bot.send_message(
        message.chat.id,
        "✅ Payment received! Your movie request has been submitted.\n\n"
        "Our team will process your request shortly. You'll receive the movie file "
        "as soon as it's ready.\n\n"
        f"Your payment ID: {payment_id}\n"
        "Use /support if you have any questions."
    )
    
    # Save payment to database
    save_payment(user_id, payment_id, amount, currency)
    
    # Notify admin
    try:
        user_info = get_user_info(user_id)
        username = f"@{user_info[1]}" if user_info and user_info[1] else "No username"
        bot.send_message(
            ADMIN_ID,
            f"🎬 New Movie Request!\n\n"
            f"👤 User: {username} ({user_id})\n"
            f"💰 Amount: {amount/100} {currency}\n"
            f"🆔 Payment ID: {payment_id}\n\n"
            f"Reply to this with the movie file and '{payment_id}' as caption"
        )
    except Exception as e:
        print(f"⚠️ Failed to notify admin: {e}")
# /support command handler
@bot.message_handler(commands=['support'])
def handle_support(message):
    bot.send_message(
        message.chat.id,
        "Movie requests are non-refundable. "
        "If you have any questions, please contact our support team."
    )

if __name__ == "__main__":
    while True:
        try:
            bot.polling(none_stop=True, interval=1)  # ✅ Auto-reconnects
        except Exception as e:
            print(f"⚠️ Crash: {e}. Restarting in 5s...")
            time.sleep(5)



