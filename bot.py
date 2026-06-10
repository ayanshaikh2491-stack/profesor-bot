"""
Professor Bot — Main Telegram Bot
Run: python bot.py
"""
import logging
import asyncio
import sys
import config

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    filters, ContextTypes, CallbackQueryHandler
)

from config import (
    TELEGRAM_TOKEN, OPENAI_API_KEY, PROFESSOR_SYSTEM_PROMPT, OPENAI_MODEL, MEMORY_DIR
)
from memory import (
    get_history, add_message, clear_history,
    get_stats
)

# === LOGGING ===
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
log = logging.getLogger(__name__)

# === OPENAI SETUP ===
from openai import AsyncOpenAI
client = AsyncOpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY != "YOUR_OPENAI_API_KEY_HERE" else None


# ============================================================
#  HANDLERS
# ============================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    first_name = user.first_name or "Bhai"

    welcome = (
        f"🎯 *El Profesor is online.*\n\n"
        f"Namaste {first_name}.\n\n"
        f"Main yahan hoon teri thinking ko sharpen karne ke liye.\n"
        f"Jo bhi problem ho, jo bhi plan banana ho — hum milke karenge.\n\n"
        f"📋 *Main kya kar sakta hoon:*\n"
        f"├ /think — koi thought hai toh usko organize karein\n"
        f"├ /plan — ek proper strategy banate hain\n"
        f"├ /analyze — kisi situation ka deep analysis\n"
        f"├ /brainstorm — ideas chahiye? let's go\n"
        f"├ /contingency — backup plans ready karo\n"
        f"├ /stats — dekh kitna kaam hua hai\n"
        f"├ /clear — naye safar ki shuruaat\n"
        f"└ ya bas directly message kar — baat karte hain\n\n"
        f"*Remember:* Har plan ki ek timing hoti hai.\n"
        f"Aaj kya plan hai tera? 🧠"
    )

    try:
        await update.message.reply_photo(
            photo="https://upload.wikimedia.org/wikipedia/en/9/9a/El_profesor_La_casa_de_papel.jpg",
            caption=welcome,
            parse_mode="Markdown"
        )
    except Exception:
        await update.message.reply_text(welcome, parse_mode="Markdown")

    add_message(user.id, "user", "/start")
    add_message(user.id, "assistant", f"Welcome message sent to {first_name}")


async def think(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    thought = text.replace("/think", "", 1).strip()

    if not thought:
        await update.message.reply_text(
            "🧠 *Professor:* Bol bhai, kaunsa thought hai tere mind mein?\n\n"
            "Jaise: `/think mujhe ek app banana hai but idea clear nahi hai`\n"
            "Ya direct bhi likh sakta hai — main samajh jaaunga.",
            parse_mode="Markdown"
        )
        return

    add_message(update.effective_user.id, "user", f"[Organize my thought] {thought}")

    thinking_msg = await update.message.reply_text("🧠 *Professor is analyzing...*", parse_mode="Markdown")

    professor_response = await get_professor_response(
        update.effective_user.id,
        f"Mere paas yeh thought hai: \"{thought}\". "
        f"Ise organize kar, structure de, aur bata ki aage kya sochna chahiye. "
        f"Professor ki tarah logical breakdown de."
    )

    await thinking_msg.delete()
    await update.message.reply_text(professor_response, parse_mode="Markdown")


async def plan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    goal = text.replace("/plan", "", 1).strip()

    if not goal:
        await update.message.reply_text(
            "📋 *Professor:* Plan banana hai? Bata kiska?\n\n"
            "Jaise: `/plan ek business shuru karna hai`\n"
            "Ya: `/plan website banana hai 1 mahine mein`\n\n"
            "Jitna detail doge, utna hi solid plan banaunga.",
            parse_mode="Markdown"
        )
        return

    add_message(update.effective_user.id, "user", f"[Plan] {goal}")

    thinking_msg = await update.message.reply_text(
        "📋 *Professor is strategizing...*\n"
        "├ Phase 1: Understanding the objective\n"
        "├ Phase 2: Resource assessment\n"
        "├ Phase 3: Timeline planning\n"
        "└ Phase 4: Contingency preparation",
        parse_mode="Markdown"
    )

    professor_response = await get_professor_response(
        update.effective_user.id,
        f"Mujhe is cheez ke liye ek detailed strategic plan chahiye: \"{goal}\". "
        f"Professor jaisa plan de: Phases, Timeline, Resources, Risks, Contingencies. "
        f"Speak in Hinglish."
    )

    await thinking_msg.delete()
    await update.message.reply_text(professor_response, parse_mode="Markdown")


async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    situation = text.replace("/analyze", "", 1).strip()

    if not situation:
        await update.message.reply_text(
            "🔍 *Professor:* Kya analyze karna hai?\n\n"
            "Jaise: `/analyze mera business kyu nahi chal raha`\n"
            "Ya: `/analyze is partnership mein kya risks hain`",
            parse_mode="Markdown"
        )
        return

    add_message(update.effective_user.id, "user", f"[Analyze] {situation}")

    thinking_msg = await update.message.reply_text(
        "🔍 *Professor is analyzing from all angles...*",
        parse_mode="Markdown"
    )

    professor_response = await get_professor_response(
        update.effective_user.id,
        f"Is situation ka deep analysis karo: \"{situation}\". "
        f"Professor jaisa analysis de: multiple perspectives, hidden factors, risks, opportunities. "
        f"Speak in Hinglish."
    )

    await thinking_msg.delete()
    await update.message.reply_text(professor_response, parse_mode="Markdown")


async def brainstorm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    topic = text.replace("/brainstorm", "", 1).strip()

    if not topic:
        await update.message.reply_text(
            "💡 *Professor:* Kis cheez ke liye ideas chahiye?\n\n"
            "Jaise: `/brainstorm ek app ke features`\n"
            "Ya: `/brainstorm marketing ideas low budget mein`",
            parse_mode="Markdown"
        )
        return

    add_message(update.effective_user.id, "user", f"[Brainstorm] {topic}")

    thinking_msg = await update.message.reply_text(
        "💡 *Professor is opening the idea vault...*",
        parse_mode="Markdown"
    )

    professor_response = await get_professor_response(
        update.effective_user.id,
        f"Is topic pe ideas chahiye: \"{topic}\". "
        f"Creative but practical ideas de. Har idea ka pros/cons bata. "
        f"Speak in Hinglish."
    )

    await thinking_msg.delete()
    await update.message.reply_text(professor_response, parse_mode="Markdown")


async def contingency(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    scenario = text.replace("/contingency", "", 1).strip()

    if not scenario:
        await update.message.reply_text(
            "🔄 *Professor:* Kiske liye backup plans chahiye?\n\n"
            "Professor ke paas hamesha Plan B, C, D ready rehte hain.\n"
            "Jaise: `/contingency agar app launch fail ho jaye`\n"
            "Ya: `/contingency client ne budget cancel kar diya`",
            parse_mode="Markdown"
        )
        return

    add_message(update.effective_user.id, "user", f"[Contingency] {scenario}")

    thinking_msg = await update.message.reply_text(
        "🔄 *Professor is preparing backup plans...*\n"
        "├ Plan B: Alternative approach\n"
        "├ Plan C: Fallback strategy\n"
        "└ Plan D: Emergency exit",
        parse_mode="Markdown"
    )

    professor_response = await get_professor_response(
        update.effective_user.id,
        f"Is scenario ke liye backup plans chahiye: \"{scenario}\". "
        f"Plan A (current), Plan B (alternative), Plan C (fallback), Plan D (emergency). "
        f"Har plan ke pros/cons aur trigger conditions bata. Speak in Hinglish."
    )

    await thinking_msg.delete()
    await update.message.reply_text(professor_response, parse_mode="Markdown")


async def show_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    stats = get_stats(update.effective_user.id)

    if stats["total_messages"] == 0:
        await update.message.reply_text(
            "📊 *Professor:* Koi history nahi hai abhi tak.\n"
            "Baat shuru karte hain pehle!",
            parse_mode="Markdown"
        )
        return

    msg = (
        f"📊 *Professor — Session Stats*\n\n"
        f"├ Total messages: `{stats['total_messages']}`\n"
        f"├ Tune bheje: `{stats['user_messages']}`\n"
        f"├ Maine bheje: `{stats['bot_messages']}`\n"
        f"├ Pehli baat: `{stats['first_seen'][:10] if stats['first_seen'] else 'N/A'}`\n"
        f"└ Aakhri baat: `{stats['last_seen'][:10] if stats['last_seen'] else 'N/A'}`\n\n"
        f"Kaam chal raha hai bhai! 🔥"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")


async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("✅ Haan, clear karo", callback_data="clear_yes"),
            InlineKeyboardButton("❌ Nahi, rehne do", callback_data="clear_no"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "⚠️ *Professor:* Kya tum saari baatein delete karna chahte ho?\n"
        "Professor ki memory mein jo record hai woh jayega permanently.",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )


async def clear_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "clear_yes":
        clear_history(update.effective_user.id)
        await query.edit_message_text(
            "🧹 *Professor:* Sab clear. Naye safar ki shuruaat.\n\n"
            "Jo sochta hai woh kar sakta hai — bas sahi plan chahiye.\n"
            "Bol bhai, aage kya?",
            parse_mode="Markdown"
        )
    else:
        await query.edit_message_text(
            "👌 *Professor:* Theek hai, sab rahne do.\n"
            "History mein rakhte hain, kabhi kaam aayegi.",
            parse_mode="Markdown"
        )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "🎯 *El Profesor — Commands*\n\n"
        "🧠 `/think` — Koi thought hai? Organize karein\n"
        "📋 `/plan` — Strategic plan banayein\n"
        "🔍 `/analyze` — Deep analysis karein\n"
        "💡 `/brainstorm` — Ideas chahiye?\n"
        "🔄 `/contingency` — Backup plans ready karein\n"
        "📊 `/stats` — Apni progress dekhein\n"
        "🧹 `/clear` — Naye safar ki shuruaat\n"
        "❓ `/help` — Yeh menu\n\n"
        "Ya bas *direct message karo* — Professor se baat karo jaise normally karte ho.\n"
        "Main har baat mein strategy dhoondh ke deta hoon! 💪"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")


# ============================================================
#  CORE AI LOGIC
# ============================================================

async def get_professor_response(user_id: int, user_message: str) -> str:
    if not client:
        return (
            "🧠 *Professor:* Arre bhai! OpenAI API key set nahi hai!\n\n"
            "Setup karne ke liye config.py mein OPENAI_API_KEY daal do:\n"
            "Ya environment variable set karo: `set OPENAI_API_KEY=sk-...`\n\n"
            "Phir `python bot.py` run karo! 💪"
        )

    try:
        history = get_history(user_id)

        messages = [{"role": "system", "content": PROFESSOR_SYSTEM_PROMPT}]
        recent_history = history[-20:] if len(history) > 20 else history
        for msg in recent_history:
            if msg["role"] in ("user", "assistant"):
                messages.append({"role": msg["role"], "content": msg["content"]})

        messages.append({"role": "user", "content": user_message})

        response = await client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=messages,
            max_tokens=1000,
            temperature=0.7,
        )

        reply = response.choices[0].message.content

        add_message(user_id, "user", user_message)
        add_message(user_id, "assistant", reply)

        return reply

    except Exception as e:
        log.error(f"OpenAI error: {e}")
        return (
            f"🧠 *Professor:* Kuch technical error aa gaya ({type(e).__name__}).\n\n"
            f"Check karo:\n"
            f"├ API key sahi hai?\n"
            f"├ Internet chal raha hai?\n"
            f"└ Phir se try karo bhai."
        )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text

    if not text:
        return

    log.info(f"Message from {user.first_name} ({user.id}): {text[:50]}...")

    asyncio.create_task(send_typing(update.effective_chat.id, context.bot))
    await asyncio.sleep(0.5)

    professor_response = await get_professor_response(user.id, text)

    if len(professor_response) > 4000:
        parts = [professor_response[i:i+4000] for i in range(0, len(professor_response), 4000)]
        for part in parts:
            await update.message.reply_text(part, parse_mode="Markdown")
    else:
        await update.message.reply_text(professor_response, parse_mode="Markdown")


async def send_typing(chat_id, bot):
    for _ in range(3):
        try:
            await bot.send_chat_action(chat_id=chat_id, action="typing")
            await asyncio.sleep(1.5)
        except Exception:
            break


# ============================================================
#  MAIN
# ============================================================

async def post_init(app: Application):
    log.info("=" * 50)
    log.info("🎯 PROFESSOR BOT — STARTING UP")
    log.info("=" * 50)

    if TELEGRAM_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN_HERE":
        log.error("TELEGRAM TOKEN not set!")
        log.error("Set environment variable: PROFESSOR_BOT_TOKEN")
        log.error("Or edit config.py directly")
        return False

    if not client:
        log.warning("OPENAI not configured — will use fallback responses")
    else:
        log.info(f"OpenAI configured (model: {OPENAI_MODEL})")

    log.info(f"Memory directory: {config.MEMORY_DIR}")
    log.info("Bot ready. Press Ctrl+C to stop.")
    log.info("=" * 50)
    return True


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log.error(f"Update {update} caused error {context.error}")
    try:
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "⚠️ *Professor:* Kuch gadbad ho gayi.\n"
                "Chinta mat kar, Plan B pe switch karte hain.\n"
                "Thodi der mein try kar bhai.",
                parse_mode="Markdown"
            )
    except Exception:
        pass


def main():
    if TELEGRAM_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN_HERE":
        print("""
  TELEGRAM BOT TOKEN NOT SET!

  1. Go to @BotFather on Telegram
  2. Create a new bot: /newbot
  3. Copy the token
  4. Set it and run again:

     set PROFESSOR_BOT_TOKEN=your_token_here
     python bot.py

  Or edit config.py and put token there directly
        """)
        return

    app = Application.builder() \
        .token(TELEGRAM_TOKEN) \
        .post_init(post_init) \
        .build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("think", think))
    app.add_handler(CommandHandler("plan", plan))
    app.add_handler(CommandHandler("analyze", analyze))
    app.add_handler(CommandHandler("brainstorm", brainstorm))
    app.add_handler(CommandHandler("contingency", contingency))
    app.add_handler(CommandHandler("stats", show_stats))
    app.add_handler(CommandHandler("clear", clear))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(clear_callback, pattern="^clear_"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(error_handler)

    log.info("Starting Professor Bot (polling)...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
