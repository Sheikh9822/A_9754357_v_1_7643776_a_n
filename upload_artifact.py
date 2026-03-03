import os
import sys
import time
import asyncio
from pyrogram import Client

last_update_time = 0

async def progress(current, total):
    global last_update_time
    now = time.time()
    
    # Print progress to GitHub Actions log every 3 seconds to avoid spam
    if now - last_update_time > 3 or current == total:
        percent = (current / total) * 100
        cur_mb = current / (1024 * 1024)
        tot_mb = total / (1024 * 1024)
        print(f"Uploading... {percent:.1f}% ({cur_mb:.2f}MB / {tot_mb:.2f}MB)")
        last_update_time = now

async def main():
    # Load credentials from environment variables
    api_id = os.getenv("API_ID")
    api_hash = os.getenv("API_HASH")
    bot_token = os.getenv("BOT_TOKEN")
    chat_id = os.getenv("CHAT_ID")
    file_path = os.getenv("FILE_PATH")

    if not all([api_id, api_hash, bot_token, chat_id, file_path]):
        print("❌ ERROR: Missing one or more environment variables.")
        sys.exit(1)

    if not os.path.exists(file_path):
        print(f"❌ ERROR: File not found -> {file_path}")
        sys.exit(1)

    # Initialize Pyrogram Client in-memory (no session file saved on the runner)
    app = Client(
        "github_artifact_uploader",
        api_id=int(api_id),
        api_hash=api_hash,
        bot_token=bot_token,
        in_memory=True
    )

    file_name = os.path.basename(file_path)
    file_size = os.path.getsize(file_path) / (1024 * 1024)

    async with app:
        print(f"🚀 Starting upload of {file_name} ({file_size:.2f} MB) to Chat ID: {chat_id}")
        
        try:
            await app.send_document(
                chat_id=int(chat_id),
                document=file_path,
                caption=f"📦 **GitHub Artifact Uploaded**\n\n📁 **File:** `{file_name}`\n⚖️ **Size:** `{file_size:.2f} MB`",
                progress=progress
            )
            print("\n✅ Upload successfully completed!")
        except Exception as e:
            print(f"\n❌ FAILED to upload: {e}")
            sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())