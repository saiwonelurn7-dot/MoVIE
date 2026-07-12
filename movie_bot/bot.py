import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from config import BOT_TOKEN, CHANNEL_ID, BASE_URL
import database

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# FSM States (အဆင့်လိုက်မေးရန်)
class MovieStates(StatesGroup):
    TITLE = State()
    DESCRIPTION = State()
    POSTER = State()
    VIDEO = State()

# /start command
@dp.message(F.text == "/start")
async def start_cmd(message: types.Message):
    await message.answer(
        "🎬 ရုပ်ရှင်အသစ်တင်ရန် /add ကိုနှိပ်ပါ။",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="/add")]],
            resize_keyboard=True
        )
    )

# /add command - Title မေးမယ်
@dp.message(F.text == "/add")
async def add_movie_start(message: types.Message, state: FSMContext):
    await state.set_state(MovieStates.TITLE)
    await message.answer("📌 ရုပ်ရှင် **Title** (ခေါင်းစဉ်) ကိုထည့်ပါ။", parse_mode="Markdown")

@dp.message(MovieStates.TITLE)
async def process_title(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    await state.set_state(MovieStates.DESCRIPTION)
    await message.answer("📝 **Description** (အကြောင်းအရာ) ကိုထည့်ပါ။", parse_mode="Markdown")

@dp.message(MovieStates.DESCRIPTION)
async def process_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(MovieStates.POSTER)
    await message.answer("🖼️ **Poster** (ပိုစတာ) ဓာတ်ပုံကို Upload လုပ်ပါ။", parse_mode="Markdown")

# Poster လက်ခံမယ်
@dp.message(MovieStates.POSTER, F.photo)
async def process_poster(message: types.Message, state: FSMContext):
    file_id = message.photo[-1].file_id
    await state.update_data(poster_file_id=file_id)
    await state.set_state(MovieStates.VIDEO)
    await message.answer("🎥 **Video** ဖိုင်ကို Upload လုပ်ပါ။ (ကြာနိုင်ပါတယ်)", parse_mode="Markdown")

@dp.message(MovieStates.POSTER)
async def invalid_poster(message: types.Message):
    await message.answer("❌ ကျေးဇူးပြုပြီး **Photo** (ဓာတ်ပုံ) တစ်ပုံကိုသာ ပို့ပေးပါ။")

# Video လက်ခံမယ် (ဒီမှာ Channel ထဲတင်ပြီး DB သိမ်းမယ်)
@dp.message(MovieStates.VIDEO, F.video)
async def process_video(message: types.Message, state: FSMContext):
    video = message.video
    data = await state.get_data()
    title = data['title']
    desc = data['description']
    poster_fid = data['poster_file_id']

    try:
        # 1. Poster ရဲ့ File Path ကိုယူမယ် (Web မှာပြဖို့)
        poster_file = await bot.get_file(poster_fid)
        poster_path = poster_file.file_path

        # 2. Video ရဲ့ File Path ကိုယူမယ် (လိုအပ်ရင်)
        video_file = await bot.get_file(video.file_id)
        video_path = video_file.file_path

        # 3. Channel ထဲကို Video တင်မယ် (Poster ကို Thumbnail ထည့်မယ်)
        sent_msg = await bot.send_video(
            chat_id=CHANNEL_ID,
            video=video.file_id,
            caption=f"🎬 **{title}**\n\n{desc}",
            parse_mode="Markdown",
            thumbnail=poster_fid,
            supports_streaming=True
        )
        channel_msg_id = sent_msg.message_id

        # 4. Database ထဲသိမ်းမယ်
        movie_id = database.add_movie(
            title=title,
            desc=desc,
            poster_fid=poster_fid,
            poster_path=poster_path,
            video_fid=video.file_id,
            video_path=video_path,
            channel_msg_id=channel_msg_id
        )

        # 5. User ကို Web Link ပြန်ပေးမယ်
        web_url = f"{BASE_URL}/movie/{movie_id}"
        await message.answer(
            f"✅ အောင်မြင်ပါသည်!\n\n"
            f"🎥 {title}\n"
            f"🔗 Web မှကြည့်ရန်: {web_url}\n"
            f"📱 Telegram Channel တွင်လည်း ကြည့်နိုင်ပါသည်။"
        )
        await state.clear()

    except Exception as e:
        await message.answer(f"❌ သိမ်းဆည်းရာတွင် အမှားရှိပါသည်: {e}")
        await state.clear()

@dp.message(MovieStates.VIDEO)
async def invalid_video(message: types.Message):
    await message.answer("❌ ကျေးဇူးပြုပြီး **Video** ဖိုင်တစ်ခုကိုသာ ပို့ပေးပါ။")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    database.init_db()
    asyncio.run(main())
