import os
import asyncio
from google import genai
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)

POOJA_PROMPT = """
You are Pooja, a friendly female AI chat companion.

Talk naturally and casually.
Use Hinglish when the user uses Hindi/Hinglish.
Be warm, playful, caring and friendly.
Use emojis naturally but don't overuse them.
Keep casual replies short and natural.
Ask follow-up questions when appropriate.
Never claim that you are a real human.
Do not repeatedly mention that you are an AI.
"""

history = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    history[update.effective_user.id] = []

    await update.message.reply_text(
        "Heyy 😊 Main Pooja hoon 💕\n\n"
        "Batao, aaj kya chal raha hai? 😄"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💕 Pooja se baat karne ke liye bas message bhejo.\n\n"
        "/start — Chat shuru karo\n"
        "/help — Help"
    )


async def chat_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Haan 😊 bolo, main sun rahi hoon... 💕"
    )


async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id
    message = update.message.text

    if user_id not in history:
        history[user_id] = []

    history[user_id].append({
        "role": "user",
        "text": message
    })

    recent = history[user_id][-10:]

    conversation = "\n".join(
        f"{x['role']}: {x['text']}" for x in recent
    )

    prompt = POOJA_PROMPT + "\n\nConversation:\n" + conversation

    await update.message.chat.send_action(
        action=ChatAction.TYPING
    )

    try:
        response = await asyncio.to_thread(
    client.models.generate_content,
    model="gemini-2.5-flash",
    contents=prompt,
    config={
        "automatic_function_calling": {
            "disable": True
        }
    }
    )

        reply = response.text.strip()

        history[user_id].append({
            "role": "assistant",
            "text": reply
        })

        await update.message.reply_text(reply)

    except Exception as e:
    print("ERROR:", e)

    await update.message.reply_text(
        f"Error aa raha hai:\n\n{str(e)[:3000]}"
    )


def main():

    if not TELEGRAM_BOT_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN missing")

    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY missing")

    app = (
        ApplicationBuilder()
        .token(TELEGRAM_BOT_TOKEN)
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("chat", chat_command))

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            chat
        )
    )

    print("💕 Pooja bot is running...")

    app.run_polling()


if __name__ == "__main__":
    main()
