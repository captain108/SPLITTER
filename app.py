import os
import json
from datetime import datetime, timedelta
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

# === CONFIG ===
api_id = 21845583  # Replace with your API ID
api_hash = "081a3cc51a428ad292be0be4d4f4f975"
bot_token = "7863454586:AAHHe-yWzUTqPW9Wjn8YhDo2K_DyZblGQHg"
ADMIN_ID = 7597393283
TRIAL_LIMIT = 2
SUB_FILE = "subscriptions1.json"
CREDIT = "\n\n🤖 Powered by @captainpapaji"

app = Client("txtbot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)
user_sessions = {}
trial_uses = {}

# === SUBSCRIPTION ===
def load_subs():
    if os.path.exists(SUB_FILE):
        with open(SUB_FILE, "r") as f:
            return json.load(f)
    return {}

def save_subs(data):
    with open(SUB_FILE, "w") as f:
        json.dump(data, f, indent=2)

def is_subscribed(uid):
    subs = load_subs()
    entry = subs.get(str(uid))
    if not entry:
        return False
    exp = datetime.strptime(entry["expires"], "%Y-%m-%d %H:%M:%S")
    return datetime.now() < exp

def add_sub(uid, days, plan="pro"):
    subs = load_subs()
    expiry = datetime.now() + timedelta(days=days)
    subs[str(uid)] = {"expires": expiry.strftime("%Y-%m-%d %H:%M:%S"), "plan": plan}
    save_subs(subs)

def remove_sub(uid):
    subs = load_subs()
    if str(uid) in subs:
        del subs[str(uid)]
        save_subs(subs)

def sub_status(uid):
    subs = load_subs()
    entry = subs.get(str(uid))
    if not entry:
        return "❌ No active subscription." + CREDIT
    expiry = datetime.strptime(entry["expires"], "%Y-%m-%d %H:%M:%S")
    remaining = expiry - datetime.now()
    return f"✅ Plan: {entry['plan']}\n⏳ Expires in {remaining.days} days" + CREDIT

def is_trial_allowed(uid):
    return trial_uses.get(str(uid), 0) < TRIAL_LIMIT

def use_trial(uid):
    trial_uses[str(uid)] = trial_uses.get(str(uid), 0) + 1

def unsub_msg():
    return (
        "❌ You're not subscribed or your subscription has expired.\n\n"
        "📦 Subscription Plans:\n"
        "🗓 1 Day – ₹30\n"
        "📅 1 Week – ₹180\n"
        "📆 1 Year – ₹1500\n\n"
        "💬 Contact @captainpapaji to activate." + CREDIT
    )

# === UI ===
def menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📤 Split TXT File", callback_data="split_txt")],
        [InlineKeyboardButton("📥 Merge TXT Files", callback_data="merge_txt")]
    ])

def back_btn():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="back")]])

# === COMMANDS ===
@app.on_message(filters.command("start"))
async def start(client, message: Message):
    uid = message.from_user.id
    if not is_subscribed(uid) and not is_trial_allowed(uid):
        return await message.reply(unsub_msg())
    user_sessions[uid] = {}
    await message.reply("👋 Welcome! Choose an option:" + CREDIT, reply_markup=menu())

@app.on_message(filters.command("checksub"))
async def check_sub(client, message: Message):
    await message.reply(sub_status(message.from_user.id))

@app.on_message(filters.command("plans"))
async def plans(client, message: Message):
    await message.reply(unsub_msg())

@app.on_message(filters.command("addsub") & filters.user(ADMIN_ID))
async def add_sub_cmd(client, message: Message):
    try:
        _, uid, days = message.text.split()
        add_sub(int(uid), int(days))
        await message.reply("✅ Subscription added." + CREDIT)
    except:
        await message.reply("❌ Usage: /addsub <user_id> <days>" + CREDIT)

@app.on_message(filters.command("extend") & filters.user(ADMIN_ID))
async def extend_sub_cmd(client, message: Message):
    try:
        _, uid, days = message.text.split()
        add_sub(int(uid), int(days))
        await message.reply("✅ Subscription extended." + CREDIT)
    except:
        await message.reply("❌ Usage: /extend <user_id> <days>" + CREDIT)

@app.on_message(filters.command("removesub") & filters.user(ADMIN_ID))
async def remove_sub_cmd(client, message: Message):
    try:
        _, uid = message.text.split()
        remove_sub(int(uid))
        await message.reply("🗑️ Subscription removed." + CREDIT)
    except:
        await message.reply("❌ Usage: /removesub <user_id>" + CREDIT)

@app.on_message(filters.command("listsubs") & filters.user(ADMIN_ID))
async def list_subs(client, message: Message):
    subs = load_subs()
    if not subs:
        return await message.reply("📭 No active subscriptions." + CREDIT)
    msg = "👥 Active Subscribers:\n\n"
    sorted_subs = sorted(subs.items(), key=lambda x: x[1]["expires"])
    for uid, info in sorted_subs:
        try:
            user = await app.get_users(int(uid))
            name = f"{user.first_name or ''} {user.last_name or ''}".strip()
            username = f"@{user.username}" if user.username else ""
        except:
            name = "Unknown"
            username = ""
        msg += f"👤 {name} {username} ({uid}) | {info['plan']} | Expires: {info['expires']}\n"
    msg += f"\n📊 Total Subscribers: {len(subs)}" + CREDIT
    await message.reply(msg)

# === CALLBACK HANDLER ===
@app.on_callback_query()
async def handle_callback(client, cb):
    uid = cb.from_user.id
    if not is_subscribed(uid):
        if is_trial_allowed(uid):
            use_trial(uid)
        else:
            return await cb.message.reply(unsub_msg())

    data = cb.data
    if data == "split_txt":
        user_sessions[uid] = {"mode": "split_txt"}
        await cb.message.reply("📤 Send the `.txt` file to split." + CREDIT, reply_markup=back_btn())

    elif data == "merge_txt":
        user_sessions[uid] = {"mode": "merge_txt", "files": [], "awaiting": "merge_count"}
        await cb.message.reply("🔢 How many `.txt` files to merge?" + CREDIT, reply_markup=back_btn())

    elif data == "back":
        user_sessions[uid] = {}
        await cb.message.reply("🔙 Back to main menu:" + CREDIT, reply_markup=menu())

    elif data in ["by_lines", "by_files"]:
        s = user_sessions.get(uid)
        if not s or "txt_file" not in s:
            return
        s["split_type"] = "by_lines" if data == "by_lines" else "by_files"
        s["awaiting"] = "split_number"
        msg = "✍️ Enter lines per file:" if data == "by_lines" else "✍️ Total number of split files:"
        await cb.message.reply(msg + CREDIT, reply_markup=back_btn())

    await cb.answer()

# === DOCUMENTS ===
@app.on_message(filters.document)
async def handle_file(client, message: Message):
    uid = message.from_user.id
    s = user_sessions.get(uid)
    if not s:
        return await message.reply("❗ Use /start first." + CREDIT)

    file_path = await message.download()

    if s.get("mode") == "split_txt":
        s["txt_file"] = file_path
        s["awaiting"] = "split_choice"
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔢 By lines", callback_data="by_lines")],
            [InlineKeyboardButton("📁 By files", callback_data="by_files")],
            [InlineKeyboardButton("🔙 Back", callback_data="back")]
        ])
        await message.reply("Choose split type:" + CREDIT, reply_markup=keyboard)

    elif s.get("mode") == "merge_txt" and "merge_total" in s:
        s["files"].append(file_path)
        if len(s["files"]) < s["merge_total"]:
            await message.reply(f"📥 Received {len(s['files'])}/{s['merge_total']} files." + CREDIT)
        else:
            out = "merged_output.txt"
            with open(out, "w") as merged:
                for f in s["files"]:
                    with open(f, "r") as file:
                        merged.writelines(file.readlines())
                        merged.write("\n")
            await message.reply_document(out, caption="✅ Merged file is ready." + CREDIT)
            os.remove(out)
            for f in s["files"]:
                os.remove(f)
            user_sessions.pop(uid)

# === TEXT INPUT ===
@app.on_message(filters.text & ~filters.command(["start", "plans", "checksub", "addsub", "extend", "removesub", "listsubs"]))
async def handle_text(client, message: Message):
    uid = message.from_user.id
    s = user_sessions.get(uid)
    if not s or "awaiting" not in s:
        return
    try:
        if s["awaiting"] == "merge_count":
            s["merge_total"] = int(message.text.strip())
            s["awaiting"] = None
            await message.reply(f"📥 Now send {s['merge_total']} `.txt` files." + CREDIT, reply_markup=back_btn())

        elif s["awaiting"] == "split_number":
            num = int(message.text.strip())
            with open(s["txt_file"], "r") as f:
                lines = f.readlines()

            if s["split_type"] == "by_lines":
                chunks = [lines[i:i+num] for i in range(0, len(lines), num)]
            else:
                size = len(lines) // num + (len(lines) % num > 0)
                chunks = [lines[i:i+size] for i in range(0, len(lines), size)]

            for i, chunk in enumerate(chunks, 1):
                fname = f"part_{i}.txt"
                with open(fname, "w") as out:
                    out.writelines(chunk)
                await message.reply_document(fname, caption=f"✅ Part {i}" + CREDIT)
                os.remove(fname)

            os.remove(s["txt_file"])
            user_sessions.pop(uid)

    except Exception as e:
        await message.reply(f"❌ Error: {e}" + CREDIT)
        user_sessions.pop(uid)

# === START BOT ===
app.run()
