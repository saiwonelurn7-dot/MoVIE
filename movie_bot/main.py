import threading
import asyncio
import database
from web import app
from bot import dp, bot

# Flask App ကို Background Thread နဲ့ဖွင့်မယ်
def run_flask():
    app.run(host='0.0.0.0', port=5000)

# Telegram Bot ကို Main Thread နဲ့ဖွင့်မယ်
async def run_bot():
    await dp.start_polling(bot)

if __name__ == "__main__":
    database.init_db()
    
    # Flask ကို နောက်ခံမှာ စဖွင့်
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    # Bot ကိုစဖွင့် (ဒါက အဓိက အလုပ်လုပ်နေမယ်)
    print("🤖 Bot and Web Server are running on Render...")
    asyncio.run(run_bot())
