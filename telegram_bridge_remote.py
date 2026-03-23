# ------------------------------------------------------------------------------
# OpenClaw: The Mobile AI Agent Gateway (Grok Intelligence Integrated)
# ------------------------------------------------------------------------------
import os
import sys
import logging
import asyncio
import subprocess
import re
import json
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from datetime import datetime
from openai import OpenAI

# CONFIGURATION
TOKEN = "8571904781:AAEhaViQiEihWOHShd0a0ywJ0BMufSh13p8"
PORTFOLIO_DIR = "/home/nishan/portfolio"
ADMIN_FILE = os.path.join(PORTFOLIO_DIR, "admin_id.txt")
CONFIG_FILE = os.path.join(PORTFOLIO_DIR, "claw_config.json")
NO_OUTPUT_MSG = "[No Output]"

# Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("OpenClaw")


# Debug log for server startup
DEBUG_LOG = os.path.join(PORTFOLIO_DIR, "bot_health.log")
with open(DEBUG_LOG, 'a') as f: f.write(f"\n[{datetime.now()}] Bot Script Started\n")


def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f: return json.load(f)
        except Exception as e:
            logger.error(f"Config load error: {e}")
    return {"grok_key": None}

def get_admin():
    if os.path.exists(ADMIN_FILE):
        try:
            with open(ADMIN_FILE, 'r') as f: return int(f.read().strip())
        except Exception: return None
    return None


def get_grok_client():
    config = load_config()
    key = config.get("grok_key")
    if key:
        return OpenAI(api_key=key, base_url="https://api.x.ai/v1")
    return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    admin = get_admin()
    
    if not admin:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, lambda: open(ADMIN_FILE, 'w').write(str(user_id)))
        admin = user_id
    
    if user_id != admin:
        await update.message.reply_text("⛔ Security Lock Active.")
        return


    kb = [["📊 Status", "🧼 Clean"], ["🎯 Sync Challenge", "📖 Help"]]
    markup = ReplyKeyboardMarkup(kb, resize_keyboard=True)
    await update.message.reply_text(
        "🚀 **OpenClaw Multi-Agent Command Center Online.**\n\n"
        "I am your dedicated **Mobile Agent/Analytical Assistant**. Grok Intelligence is now active.\n\n"
        "⚡ **Capabilities:**\n"
        "- **Chat**: Just type! (Powered by Grok)\n"
        "- **Shell**: `$ [cmd]` (e.g. `$ ls -la`)\n"
        "- **Python**: ```python [code] ```\n"
        "- **Image**: Send photos for surgical cleaning and sync.",
        reply_markup=markup, parse_mode='Markdown'
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    admin = get_admin()
    
    if not admin:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, lambda: open(ADMIN_FILE, 'w').write(str(user_id)))
        admin = user_id

    if user_id != admin: return

    
    text = update.message.text
    if not text: return
    logger.info(f"Received: {text}")

    # 1. Shell Command Handler ($)
    if text.startswith("$"):
        cmd = text[1:].strip()
        await update.message.reply_text(f"🐚 **Running Shell...**\n`{cmd}`", parse_mode='Markdown')
        try:
            loop = asyncio.get_event_loop()
            res = await loop.run_in_executor(None, lambda: subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15))
            output = (res.stdout + res.stderr).strip() or NO_OUTPUT_MSG
            await update.message.reply_text(f"🏁 **Output:**\n```\n{output[:3500]}\n```", parse_mode='Markdown')
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {e}")
        return


    # 2. Python Code Execution
    if "```" in text:
        code = re.sub(r'```python|```', '', text).strip()
        await update.message.reply_text("🐍 **Executing Python...**", parse_mode='Markdown')
        try:
            tmp_file = f"/tmp/claw_exec_{datetime.now().strftime('%H%M%S')}.py"
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, lambda: open(tmp_file, 'w').write(code))
            res = await loop.run_in_executor(None, lambda: subprocess.run([sys.executable, tmp_file], capture_output=True, text=True, timeout=15))
            output = (res.stdout + res.stderr).strip() or NO_OUTPUT_MSG
            await update.message.reply_text(f"📝 **Result:**\n```\n{output[:3500]}\n```", parse_mode='Markdown')
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {e}")
        return


    # 3. Quick Actions
    if text.lower() in ["status", "📊 status"]:
        loop = asyncio.get_event_loop()
        res = await loop.run_in_executor(None, lambda: subprocess.check_output("uptime && free -h", shell=True).decode())
        await update.message.reply_text(f"🖥️ **Server Vitals:**\n\n```\n{res}\n```", parse_mode='Markdown')
        return

    if text.lower() in ["clean", "🧼 clean"]:
        await update.message.reply_text("🧼 **Starting Deep Surgical Cleanup...**")
        await asyncio.create_subprocess_exec(sys.executable, f"{PORTFOLIO_DIR}/image_processor.py")
        return


    # 4. Agentic Intelligence (Grok or Gemini)
    config = load_config()
    key = config.get("grok_key")
    if not key:
        await update.message.reply_text("⚠️ **Brain is not configured.**\nUse /set_grok [key] to activate.")
        return

    status_msg = await update.message.reply_text("🤔 **Thinking...**")
    try:
        system_prompt = (
            "You are the OpenClaw AI Hub executing directly on the user's server. "
            "You have full terminal access to inspect files, databases, apps, and count resources. "
            "To inspect anything on the server to make your answer accurate, you MUST output exactly: "
            "[RUN_SHELL: <your bash command here>] "
            "Wait for the backend framework to execute it and return the answer back in the next turn."
        )
        
        # Initialize loop variables
        max_loops = 3
        current_input = text
        conversation_history_gemini = [{"parts": [{"text": current_input}]}] if key.startswith("AIzaSy") else []
        conversation_history_grok = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": current_input}
        ] if not key.startswith("AIzaSy") else []
        
        final_reply = ""
        
        for _ in range(max_loops):

            ai_reply = None
            
            # --- 4a. Handle Google Gemini (REST) ---
            if key.startswith("AIzaSy"):
                import requests
                models = ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-2.5-flash", "gemini-pro"]
                error_data = ""
                
                for m in models:
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={key}"
                    try:
                        resp = requests.post(
                            url, 
                            headers={'Content-Type': 'application/json'}, 
                            json={
                                "contents": conversation_history_gemini,
                                "systemInstruction": {"parts": [{"text": system_prompt}]}
                            }, 
                            timeout=15
                        )
                        res_json = resp.json()
                        if "candidates" in res_json:
                            ai_reply = res_json["candidates"][0]["content"]["parts"][0]["text"]
                            break
                        else:
                            error_data += f"\n- {m}: {res_json.get('error', {}).get('message', 'Unknown Error')}"
                    except Exception as e:
                        error_data += f"\n- {m}: {e}"
                if not ai_reply:
                     final_reply = f"❌ Gemini API Error. Checked models:{error_data}"
                     break
                     
            # --- 4b. Handle Standard xAI Grok ---
            else:
                client = get_grok_client()
                response = client.chat.completions.create(
                    model="grok-2",
                    messages=conversation_history_grok
                )
                ai_reply = response.choices[0].message.content

            # --- 4c. Parse for execution tool tags ---
            # e.g., [RUN_SHELL: ls -la]
            match = re.search(r'\[RUN_SHELL:\s*(.*?)\]', ai_reply, re.DOTALL)
            if match:
                cmd_to_run = match.group(1).strip()
                logger.info(f"Agent requested shell execution: {cmd_to_run}")
                await context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=status_msg.message_id, text=f"🐚 **Agent executing Shell...**\n`{cmd_to_run}`", parse_mode='Markdown')
                
                try:
                    res = subprocess.run(cmd_to_run, shell=True, capture_output=True, text=True, timeout=15)
                    output = (res.stdout + res.stderr).strip() or "[No Output]"
                except Exception as e:
                    output = f"Shell Execution Error: {e}"
                
                # Append to history
                if key.startswith("AIzaSy"):
                    conversation_history_gemini.append({"role": "model", "parts": [{"text": ai_reply}]})
                    conversation_history_gemini.append({"role": "user", "parts": [{"text": f"Shell Output:\n{output[:3000]}"}]})
                else:
                    conversation_history_grok.append({"role": "assistant", "content": ai_reply})
                    conversation_history_grok.append({"role": "user", "content": f"Shell Output:\n{output[:3000]}"})
                
                await context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=status_msg.message_id, text="🤔 **Agent evaluating output...**")
            else:
                final_reply = ai_reply
                break

        if not final_reply or not final_reply.strip():
            final_reply = "⚠️ **AI Empty Response Error**: The model responded with an empty content stream. This might be a direct safety block trigger on the user query."
            
        await context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=status_msg.message_id, text=final_reply)

    except Exception as e:
        await context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=status_msg.message_id, text=f"❌ AI Error: {e}")



async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    admin = get_admin()
    if user_id != admin: return
    
    msg_id = update.message.message_id
    logger.info(f"📸 Received photo update (MSG: {msg_id})")
    await update.message.reply_text(f"📸 **Image {msg_id} Detected.** Queuing for processing...")
    
    try:
        from ocr_helper import extract_challenge_info
        from image_processor import clean_image
        
        # Get highest resolution
        photo = update.message.photo[-1]
        f = await context.bot.get_file(photo.file_id)
        
        # Unique paths per message
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_filename = f"sync_{ts}_{msg_id}.jpg"
        temp_path = os.path.join(PORTFOLIO_DIR, "static", "images", temp_filename)
        
        logger.info(f"Downloading photo {msg_id} to {temp_path}")
        await f.download_to_drive(temp_path)
        
        # Offload blocking operations to executor
        loop = asyncio.get_event_loop()
        
        logger.info(f"Starting OCR/Clean for {msg_id}")
        date_id, title = await loop.run_in_executor(None, extract_challenge_info, temp_path)
        await loop.run_in_executor(None, clean_image, temp_path)
        
        target_date = date_id or datetime.now().strftime("%Y-%m-%d")
        logger.info(f"Photo {msg_id} processed. Date: {target_date}, Title: {title}")
        
        # Rename to target format
        final_filename = f"{target_date.replace('-', '')}_{msg_id}_sync.jpg"
        final_path = os.path.join(PORTFOLIO_DIR, "static", "images", final_filename)
        os.rename(temp_path, final_path)
        
        # DB Sync via Subprocess (keeping it simple for now)
        db_script = f"""
import sys
sys.path.append('{PORTFOLIO_DIR}')
from app import app, db, Challenge
with app.app_context():
    challenge = Challenge.query.filter_by(date_id='{target_date}').first()
    if not challenge: challenge = Challenge(date_id='{target_date}', title='{title or "Daily Challenge"}')
    challenge.image_path = '{final_filename}'
    db.session.add(challenge)
    db.session.commit()
"""
        await loop.run_in_executor(None, lambda: subprocess.run([sys.executable, "-c", db_script]))
        
        await update.message.reply_text(f"✅ **Challenge Synced!** (ID: {msg_id})\nDate: `{target_date}`\nWebsite updated. 🚀")
        logger.info(f"✅ Photo {msg_id} sync complete.")
        
    except Exception as e:
        logger.error(f"❌ Pipeline Error for {msg_id}: {e}", exc_info=True)
        await update.message.reply_text(f"❌ **Pipeline Error ({msg_id}):** {e}")

async def set_grok(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != get_admin(): return
    if not context.args: return
    key = context.args[0]
    with open(CONFIG_FILE, 'w') as f: json.dump({"grok_key": key}, f)
    await update.message.reply_text("✅ **Grok Intelligence Key Set.** Brain activated! 🦾")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("set_grok", set_grok))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    
    logger.info("OpenClaw Agent Hub Online.")
    with open(DEBUG_LOG, 'a') as f: f.write(f"[{datetime.now()}] Entering app.run_polling()\n")
    app.run_polling()
