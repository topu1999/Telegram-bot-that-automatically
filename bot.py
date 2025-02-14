import logging
from typing import Final
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, ContextTypes, CallbackQueryHandler, 
    ChatJoinRequestHandler, MessageHandler, filters
)
from telegram.constants import ParseMode
from telegram.error import TelegramError
from database import Database

# Welcome message
WELCOME_TEXT = (
    "👋 Welcome to our community!\n\n"
    "To get started:\n"
    "1️⃣ Please introduce yourself with a brief message\n"
    "2️⃣ After that, you'll be able to use the broadcast feature\n"
    "3️⃣ Enjoy being part of our community!"
)

# Bot token
TOKEN: Final = '7665972397:AAGkiKZRl5zz2P0VE-KKmBlj_Hyd_PsfHr8'


# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Initialize database
db = Database()

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user:
        return
        
    user_id = update.effective_user.id
    db.add_user(user_id)
    
    # Send welcome message
    await update.message.reply_text(WELCOME_TEXT)
    
    # Then show the main menu
    keyboard = [
        [
            InlineKeyboardButton("Add Channel", callback_data="add_channel"),
            InlineKeyboardButton("Add Group", callback_data="add_group")
        ],
        [InlineKeyboardButton("Broadcast Message", callback_data="broadcast")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Here are the available options:",
        reply_markup=reply_markup
    )


async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "add_channel":
        await query.message.reply_text(
            "To add a channel:\n"
            "1. Add this bot as an admin to your channel\n"
            "2. Forward any message from the channel to this bot"
        )
    elif query.data == "add_group":
        await query.message.reply_text(
            "To add a group:\n"
            "1. Add this bot as an admin to your group\n"
            "2. Send /addgroup command in the group"
        )
    elif query.data == "broadcast":
        if not db.is_admin(query.from_user.id):
            await query.message.reply_text("⚠️ Only admins can broadcast messages.")
            return
            
        help_text = (
            "📢 *Admin Broadcast*\n\n"
            "Send /broadcast followed by your message.\n"
            "You can use HTML formatting:\n"
            "• <b>bold</b>\n"
            "• <i>italic</i>\n"
            "• <u>underline</u>\n"
            "• <a href='URL'>link</a>\n\n"
            "Example: /broadcast Hello <b>everyone</b>!"
        )
        await query.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)

async def send_welcome_message(chat_id: int, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "👋 Welcome to our community!\n\n"
        "To get started:\n"
        "1️⃣ Please introduce yourself with a brief message\n"
        "2️⃣ After that, you'll be able to use the broadcast feature\n"
        "3️⃣ Enjoy being part of our community!"
    )
    await context.bot.send_message(chat_id=chat_id, text=welcome_text)

async def handle_join_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    join_request = update.chat_join_request
    try:
        await join_request.approve()
        # Send welcome message after approving join request
        await send_welcome_message(join_request.user_chat_id, context)
    except Exception as e:
        logging.error(f"Error handling join request: {e}")

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user:
        return
    
    user_id = update.effective_user.id
    if not db.is_admin(user_id):
        await update.message.reply_text("⚠️ This command is only available for admins.")
        return
        
    stats = db.get_stats()
    status_text = (
        "📊 Bot Status:\n\n"
        f"👥 Total Users: {stats['total_users']}\n"
        f"📢 Channels: {stats['total_channels']}\n"
        f"👥 Groups: {stats['total_groups']}\n"
        f"👑 Admins: {stats['total_admins']}"
    )
    await update.message.reply_text(status_text)

async def add_admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user:
        return
        
    if not db.is_admin(update.effective_user.id):
        await update.message.reply_text("⚠️ Only existing admins can add new admins.")
        return
        
    if not context.args:
        await update.message.reply_text("Please provide a user ID to add as admin.")
        return
        
    try:
        new_admin_id = int(context.args[0])
        db.add_admin(new_admin_id)
        await update.message.reply_text(f"✅ User {new_admin_id} has been added as admin.")
    except ValueError:
        await update.message.reply_text("⚠️ Please provide a valid user ID.")

async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user:
        return
    
    user_id = update.effective_user.id
    if not db.is_admin(user_id):
        await update.message.reply_text("⚠️ Only admin can broadcast messages.")
        return

    if not context.args:
        help_text = (
            "📢 How to Broadcast:\n\n"
            "1. Use the command /broadcast followed by your message\n"
            "Example: /broadcast Hello everyone!\n\n"
            "Your admin ID: " + str(user_id) + "\n"
            "Required admin ID: " + str(db.ADMIN_ID)
        )
        await update.message.reply_text(help_text)
        return

    message = ' '.join(context.args)
    users = db.get_all_users()
    
    success_count = 0
    for uid in users:
        try:
            await context.bot.send_message(chat_id=uid, text=message)
            success_count += 1
        except Exception as e:
            logging.error(f"Failed to send message to {uid}: {e}")
    
    await update.message.reply_text(f"Message broadcasted to {success_count} users.")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not update.message.text:
        return
    
    user_id = update.effective_user.id
    user_data = db.get_user_data(user_id)
    
    # If user hasn't introduced themselves yet
    if not user_data.get('has_introduced', False):
        # Mark user as introduced
        db.set_user_introduced(user_id)
        
        await update.message.reply_text(
            "✅ Thank you for introducing yourself!\n"
            "You can now use the broadcast feature."
        )
        
        keyboard = [
            [
                InlineKeyboardButton("Add Channel", callback_data="add_channel"),
                InlineKeyboardButton("Add Group", callback_data="add_group")
            ],
            [InlineKeyboardButton("Broadcast Message", callback_data="broadcast")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "Here are the available options:",
            reply_markup=reply_markup
        )


async def addgroup_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type in ['group', 'supergroup']:
        db.add_group(update.effective_chat.id)
        await update.message.reply_text("Group has been added successfully!")
    else:
        await update.message.reply_text("This command can only be used in groups!")

async def handle_forward(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.forward_from_chat:
        return
        
    chat = update.message.forward_from_chat
    if chat.type == 'channel':
        db.add_channel(chat.id)
        await update.message.reply_text(
            f"✅ Channel '{chat.title}' has been successfully added!\n"
            "I will now automatically accept join requests for this channel."
        )

def main():
    app = Application.builder().token(TOKEN).build()

    # Command handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("broadcast", broadcast_command))
    app.add_handler(CommandHandler("addgroup", addgroup_command))
    app.add_handler(CommandHandler("admin", admin_command))
    app.add_handler(CommandHandler("addadmin", add_admin_command))
    
    # Message handlers
    app.add_handler(MessageHandler(filters.FORWARDED & filters.ChatType.PRIVATE, handle_forward))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE, handle_message))
    
    # Callback query handler for buttons
    app.add_handler(CallbackQueryHandler(handle_button))
    
    # Join request handler
    app.add_handler(ChatJoinRequestHandler(handle_join_request))

    # Start the bot
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()