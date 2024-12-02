import subprocess
import sys

# لیست کتابخانه‌های مورد نیاز
required_libraries = [
    "aiohttp", "arabic_reshaper", "bidi", "beautifulsoup4", "deep_translator",
    "gtts", "khayyam", "num2words", "Pillow", "pycoingecko",
    "requests", "rubpy", "scrapy", "twisted", "google","nltk","qrcode","jdatetime"," phonenumbers"
]

# تابع برای نصب کتابخانه
def install(package):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"{package} با موفقیت نصب شد.")
    except subprocess.CalledProcessError:
        print(f"نصب {package} با خطا مواجه شد.")

# بررسی و نصب کتابخانه‌ها
for lib in required_libraries:
    try:
        __import__(lib)
    except ImportError:
        print(f"{lib} نصب نیست، در حال نصب...")
        install(lib)

# وارد کردن کتابخانه‌ها
import os
import sqlite3
import aiohttp
import re
import logging
import random
import asyncio
import shutil
from datetime import datetime, timedelta
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from bs4 import BeautifulSoup

# وارد کردن ماژول‌های پروژه
from database_bot import (
    init_db, set_learning_enabled, get_all_questions_answers, clear_knowledge_base,
    is_learning_enabled, save_question_answer, get_answer
)
from news_site import fetch_latest_news
from openweathermap import get_weather, translate_text
from find_emoji_response import (
    find_emoji_response, predictions, haqiqat, joraat, tourist_spots,
    meshedi_phrases, send_in_chunks
)
from chat_bot import (
    get_chatbot_response, get_song, fetch_estekhare, fetch_video, fetch_prof,
    fetch_audio, get_random_music_link, get_bmi_advice, calculate_bmi,
    validate_input, get_location_map, search_myket
)
from echo import chatbot
from get_ip_address import get_ip_address
from create_qr import create_qr_code
import bio_fackt_faz
from bio_fackt_faz import get_random_health_tip, get_random_quote
from phone_number import get_phone_info
from googlesearch import search
import scrapy
import prayer_times
from scrapy.crawler import CrawlerRunner
from twisted.internet import defer, reactor
from scrapy.utils.log import configure_logging
from code_runer import execute_code

# وارد کردن کتابخانه‌های با نصب مشروط
try:
    import rubpy
    from rubpy import Client, filters, utils, exceptions,Rubino
    from rubpy.types import Updates
    from rubpy.enums import ReportType
except ImportError:
    install('rubpy')
    import rubpy
    from rubpy import Client, filters, utils, exceptions
    from rubpy.types import Updates
    from rubpy.enums import ReportType

try:
    import requests
except ImportError:
    install('requests')
    import requests

try:
    from gtts import gTTS
except ImportError:
    install("gtts")
    from gtts import gTTS

try:
    from deep_translator import GoogleTranslator
except ImportError:
    install("deep_translator")
    from deep_translator import GoogleTranslator

try:
    from khayyam import JalaliDatetime
except ImportError:
    install("khayyam")
    from khayyam import JalaliDatetime

try:
    import arabic_reshaper
except ImportError:
    install("arabic_reshaper")
    import arabic_reshaper

try:
    from bidi.algorithm import get_display
except ImportError:
    install("python-bidi")
    from bidi.algorithm import get_display

try:
    from pycoingecko import CoinGeckoAPI
except ImportError:
    install("pycoingecko")
    from pycoingecko import CoinGeckoAPI

try:
    from num2words import num2words
except ImportError:
    install("num2words")
    from num2words import num2words

    
    

# ساخت بات
bot = Client(name='Ai_bot')
rubino = Rubino(bot)
# مجموعه کلمات فیلترشده
filtered_phrases = set()
choices = ["سنگ", "کاغذ", "قیچی"]
game_active = False  # وضعیت بازی
allow_warning = True
def check_warning_status():
    return allow_warning
help_ = """
سلام! به ربات میربات خوش آمدید. لطفاً دستورات ربات را در کانال ما مشاهده کنید:

@mirbotrubika
"""

    
valid_expression_pattern = r'^[\d\s\+\-\*\/\(\)]+$'

conn = sqlite3.connect('users_bot.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS users (user_id TEXT PRIMARY KEY, name TEXT)''')
conn.commit()

# تابع ذخیره نام کاربر با user_id منحصربه‌فرد
def save_user_name(user_id, name):
    try:
        cursor.execute('REPLACE INTO users (user_id, name) VALUES (?, ?)', (str(user_id), name))
        conn.commit()
    except sqlite3.Error as e:
        print("Error saving user name:", e)

# تابع بازیابی نام کاربر
def get_user_name(user_id):
    cursor.execute('SELECT name FROM users WHERE user_id = ?', (str(user_id),))
    result = cursor.fetchone()
    return result[0] if result else None



def get_all_users():
    cursor.execute('SELECT name FROM users')
    results = cursor.fetchall()
    return [row[0] for row in results]
async def get_guid():
    profile_info =await rubino.get_my_profile_info()
    profile_id=profile_info["profile"]["id"]
    return profile_id



# پیام‌های خوش‌آمدگویی و خروج
welcome_messages = [
    "🌟 یک عضو از طریق لینک به گروه افزوده شد. {name} عزیز، خوش‌آمدی! ⏰ زمان ورود: {time}",
    "🎉 سلام {name}! خوش آمدی به جمع ما! ⏰ زمان ورود: {time}",
    "🌺 {name} عزیز، به گروه خوش آمدی! امیدواریم لحظات خوبی داشته باشی. ⏰ زمان ورود: {time}",
    "✨ خوش‌آمدی {name} جان! اینجا از حضورت خوشحالیم. ⏰ زمان ورود: {time}",
    "👏 {name} جان، به گروه خوش اومدی! امیدواریم لحظات خوبی داشته باشی. ⏰ زمان ورود: {time}",
    "🌈 {name} عزیز، خوش اومدی! آماده تجربه‌های جدید هستیم! ⏰ زمان ورود: {time}",
    "🎊 {name} جان، قدمت روی چشم! امیدواریم لحظات خوبی داشته باشی. ⏰ زمان ورود: {time}",
    "💐 به گروه خوش اومدی {name}! اینجا جایی برای همه هست. ⏰ زمان ورود: {time}",
    "🤗 سلام {name}! خیلی خوشحالیم که به جمع ما پیوستی! ⏰ زمان ورود: {time}",
    "🎈 {name} عزیز، به گروه خوش‌آمدی! هر لحظه‌ات پر از شادی. ⏰ زمان ورود: {time}",
    "🌞 {name} جان، نور حضور تو جمع ما رو روشن کرد! ⏰ زمان ورود: {time}",
    "🍀 به جمع ما خوش آمدی {name}! از آشناییت خوشبختیم. ⏰ زمان ورود: {time}",
    "🎇 {name} جان، خوش‌آمدی به این گروه دوست‌داشتنی! ⏰ زمان ورود: {time}",
    "🌷 سلام {name}! حضورت در اینجا پر از لطف و شادی است. ⏰ زمان ورود: {time}",
    "🥳 {name} عزیز، خوش آمدی! امیدواریم از حضورت لذت ببری. ⏰ زمان ورود: {time}",
    "💖 {name} جان، به گروه خوش اومدی! اینجا پر از عشق و دوستی هست. ⏰ زمان ورود: {time}",
    "🌟 به جمع ما خوش آمدی {name} عزیز! از حضورت دلگرمیم. ⏰ زمان ورود: {time}",
    "🌸 {name} جان، خوش‌آمدی! لحظات شادی برات آرزو داریم. ⏰ زمان ورود: {time}",
    "🕊 {name} عزیز، خوش‌آمدی! امیدواریم بهترین لحظاتت اینجا رقم بخوره. ⏰ زمان ورود: {time}",
    "✨ {name} جان، قدمت مبارک! حضور تو باعث شادی جمع ماست. ⏰ زمان ورود: {time}",
]

# پیام‌های خداحافظی با نمایش زمان
farewell_messages = [
    "😢 {name} عزیز از گروه خداحافظی کرد. به امید دیدار دوباره! ⏰ زمان خروج: \n{time}",
    "🥀 {name} عزیز، خداحافظ! همیشه موفق باشی. ⏰ زمان خروج: \n{time}",
    "👋 {name} جان، از گروه خداحافظی کرد. به امید دیدار دوباره! ⏰ زمان خروج: \n{time}",
    "💔 {name} جان، گروه رو ترک کرد. امیدواریم دوباره ببینیمت. ⏰ زمان خروج:\n {time}",
    "😔 {name} عزیز، از گروه خارج شد. همیشه موفق و پیروز باشی! ⏰ زمان خروج:\n {time}",
    "🌹 {name} جان، به امید دیدار دوباره! برات آرزوی موفقیت می‌کنیم. ⏰ زمان خروج: \n{time}",
    "😢 {name} عزیز، با دلی گرفته از گروه خداحافظی کرد. ⏰ زمان خروج: \n{time}",
    "🌺 {name} جان، هرجا هستی موفق باشی! به امید دیدار دوباره. ⏰ زمان خروج: \n{time}",
    "👋 {name} عزیز، با امید دیدار مجدد! بدرود. ⏰ زمان خروج: \n{time}",
    "😞 {name} جان، از گروه رفتی، دلتنگت خواهیم شد! ⏰ زمان خروج:\n {time}",
    "💐 {name} عزیز، خداحافظی کردی ولی جایت در دل ماست. ⏰ زمان خروج:\n {time}",
    "🌟 {name} جان، برات روزهای خوش آرزو می‌کنیم! موفق باشی. ⏰ زمان خروج: \n{time}",
    "🥲 {name} عزیز، همیشه به یاد خواهیم داشت حضورت رو. ⏰ زمان خروج: \n{time}",
    "🌷 {name} جان، خداحافظ! همیشه تو قلب ما جا داری. ⏰ زمان خروج: \n{time}",
    "🤲 {name} عزیز، به امید دیدار دوباره. برات آرزوی خوشبختی داریم. ⏰ زمان خروج:\n {time}",
    "🖤 {name} جان، از گروه خداحافظی کردی، منتظر برگشتت می‌مونیم. ⏰ زمان خروج:\n {time}",
    "🌿 {name} عزیز، با آرزوی موفقیت بدرود. ⏰ زمان خروج: \n{time}",
    "✋ {name} جان، گروه رو ترک کردی، دلتنگت میشیم. ⏰ زمان خروج: \n{time}",
    "🍂 {name} عزیز، بدرود! همیشه موفق و پیروز باشی. ⏰ زمان خروج: \n{time}",
    "🕊 {name} جان، آرزو داریم روزهای خوبی پیش روت باشه! خداحافظ. ⏰ زمان خروج: \n {time}",
]
# الگوهای قوی‌تر برای شناسایی
welcome_patterns = [
    r"\bjoined the group\b", r"\bjoined\b", r"\bپیوست\b", 
    r"\bعضو شد\b", r"\bبه گروه اضافه شد\b", r"\bوارد گروه شد\b",
    r"\bبه جمع ما پیوست\b", r"\binvited\b", r"\binvite link\b",
    r"\bjoined group\b", r"\bاز طریق لینک\b", r"\bgroup join\b"
]

farewell_patterns = [
    r"\bleft the group\b", r"\bleft\b", r"\bخروج\b", 
    r"\bترک کرد\b", r"\bاز گروه خارج شد\b", r"\bگروه را ترک کرد\b",
    r"\bگروه را ترک\b", r"\bخداحافظ\b", r"\bleft group\b", 
    r"\bquit\b", r"\bexited\b", r"\bخداحافظی کرد\b"
]
def match_patterns(text, patterns):
    for pattern in patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False
# متغیر برای نگهداری آخرین سوال و جواب
last_question = None
last_answer = None
MAX_MESSAGE_LENGTH = 4000

# تابع برای تقسیم پیام به چند بخش
def split_message(message, max_length=MAX_MESSAGE_LENGTH):
    # اگر پیام طولانی بود، آن را به بخش‌های کوچکتر تقسیم می‌کنیم
    return [message[i:i + max_length] for i in range(0, len(message), max_length)]

music_styles = [
    "1- Pop 🎉", "2- Intense 🔥", "3- Violin 🎻", "4- Anthemic 🎺", 
    "5- Male Voice 👨‍🎤", "6- Funk 🎵", "7- Ethereal 🌌", 
    "8- Hard Rock 🤘", "9- Groovy 🎸", "10- Soul 🎷", 
    "11- Psychedelic 🌈", "12- Catchy 🎶", "13- Male Vocals 🎤", 
    "14- Japanese 🇯🇵", "15- Ambient 🌌", "16- Atmospheric ☁️", 
    "17- Synth 🎹", "18- Dreamy 🌙", "19- Electric Guitar 🎸"
]

FONT_PATHS = [
    "fonts/Arial.ttf",         # فونت انگلیسی
    "fonts/Roboto-Regular.ttf", # فونت انگلیسی
    "fonts/Vazir-Regular.ttf",  # فونت فارسی
    "fonts/IranSans.ttf",       # فونت فارسی
]
captions = [
    "ای رهبر آزاده، آماده‌ایم آماده\nتا آخرین نفس‌ها، در راهتیم دل داده",
    "دل را به نور مهر تو روشن کرده‌ایم\nجان را به عشق تو فدایی کرده‌ایم",
    "تو نور راه مایی، ای رهبر ما\nعشقت همیشه جاری است در دل ما",
    "ای سید و مولای ما، دل‌گرم به عشقت\nجان‌ها فدای راه تو، تا روز بعثت",
    "با تو مسیر عشق را پیموده‌ایم\nدر سایه‌سارت ای رهبر آسوده‌ایم",
    "مهر تو در دل ما، شعله‌ور چون خورشید\nعشق تو تا ابد، در جان ما امید",
    "تا زنده‌ایم ای رهبر عاشق\nدل‌ها به عشق تو همیشه دمساز است",
    "با تو مسیر عشق طی خواهیم کرد\nتا جان فدای راهت ای رهبر کرد",
    "ای رهبرم، در سایه‌ات آرامیم\nبا عشق تو در دل، همراه و هم‌گامیم",
    "مهر تو در دل‌ها، چون شعله‌ای جاوید\nعشق تو در این قلب، هرگز نمی‌پوسید",

    # شعرهای جدید:
    "ای رهبر ما، چراغ راهی\nدر پرتو نورت، جان پناهی",
    "عشقت در دل ما تا ابد پایدار\nبا تو دل و جانمان استوار",
    "با نفس تو زنده‌ایم ای رهبر دل‌ها\nعشق تو جاری‌ست در عمق دل‌ها",
    "تو تکیه‌گاه ما، در مسیر ایمان\nبا تو پیموده‌ایم راه به‌سوی جان",
    "رهبرا، دل به تو بسته‌ایم تا ابد\nبا نام تو، امید ما همیشه شد بلند",
    "ای رهبر دل‌ها، در سایه‌ات آرام\nعشق تو در قلب ماست همچو نور و مرام",
    "ای رهبر عشق، در پناهت دل ما\nبا تو شکوفا شده جان و دل ما",
    "در راه تو ما جان فدایی داریم\nبا مهر تو در دل، عشق خدایی داریم",
    "تو نوری در شب‌های تاریک ما\nبا تو پیمودیم راه عاشقانه تا خدا",
    "هر لحظه در سایه‌ی تو سرشاریم\nعشق تو در دل، تا ابد برقراریم",

    # شعرهای مقتدرانه:
    "ای امام ما، در نبرد با طاغوت\nعشق تو در دل‌ها، می‌سازد راه رستگاری و قوت",
    "دست‌های پر قدرت تو، بر سرمان سایه\nما با تو هستیم، تا جان در تن داریم و پایداره",
    "در ره تو ای رهبر، دل‌های ما حماسه است\nعشقت به ما قوت می‌دهد، با تو همه‌چیز ممکن است",
    "مردی از جنس ایمان و ایثار\nما را با اراده‌ات زنده‌ می‌کنی به اعتبار",
    "در حماسه‌ات ما جوش و خروش داریم\nبا تو، بر تاریکی‌ها پیروزیم و خروش داریم",
    "ای رهبر، ما را به قله‌های رفیع ببر\nبا قدرت کلامت، دنیای ظلمت را در هم بشکن",
    "تو فرمانده‌ی عشق و ایستادگی‌ای\nبا تو تا پیروزی، هم‌صدا و هم‌راستا می‌شویم",
    "هر بار که ندا می‌کنی، دل‌ها می‌تپد\nبا تو، در این راه دشوار، پیروزی مسلّم است",
    "ما نسل انقلابیم، در سختی‌ها ایستاده‌ایم\nدست در دست تو، بر همه‌ی موانع غلبه کرده‌ایم",
    "ای رهبر عزیز، تو امید ملت ما\nبا تو به سوی فردا، بی‌پروا می‌رویم و شجاعانه می‌کوشیم",

    # شعرهای ترساننده برای دشمنان:
    "ای دشمنان اسلام، در خیال باطل خود\nبیداری ما را هرگز نمی‌توانید خواب ببرید",
    "صدای نای تو، همچو طوفان است\nتا ظهور حق، ستم بر نخواهد گشت",
    "دشمنان بدانند که ما ایستاده‌ایم\nهرگز تسلیم، نه در خواب و نه در بیداری نیستیم",
    "آتش خشم ما در دل‌هاست، بیدارید\nدشمنان بدانند، ما فراموش نخواهیم کرد",
    "به کوری چشم شما، پرچم ما بلند است\nعزم ما در دل‌ها، هرگز محو نخواهد شد",
    "هرگز فراموش نخواهیم کرد ظالم را\nآینده از آن ماست، در سایه‌ی رهبرِ دلاور",
    "شما زخم‌زنندگان امیدها، بشنوید صدا\nملت ما بیدار است، در صفوف خود آماده‌است",
    "از مرزهای ما دور شوید، ای جانیان\nایران ما زنده است و زیر پرچم ایمان",
    "شما در برابر ما، چون بادی و کم‌قدرید\nعزت ما را در دل‌ها هرگز نمی‌توانید بکشید",
    "ای دشمنان جان، در خیال خام خود\nما از انقلاب، هرگز برنمی‌گردیم به عقب"
]

def get_response_from_api(user_input):
    url = "https://api.api-code.ir/gpt-4/"
    payload = {"text": user_input}

    try:
        response = requests.get(url, params=payload)
        response.raise_for_status()  # بررسی وضعیت پاسخ
        
        data = response.json()
        return data['result']  # فقط نتیجه را برمی‌گرداند

    except requests.exceptions.HTTPError as http_err:
        return f"HTTP error occurred: {http_err}"
    except requests.exceptions.RequestException as req_err:
        return f"Request error occurred: {req_err}"
    except Exception as e:
        return f"An error occurred: {e}"

# تابع برای ایجاد یک رنگ تصادفی
def random_color(brightness=255):
    return tuple(random.randint(0, brightness) for _ in range(3))

# تابع برای محاسبه میزان تضاد رنگی (contrast)
def calculate_brightness(color):
    return (color[0] * 299 + color[1] * 587 + color[2] * 114) / 1000

def is_contrasting(color1, color2):
    return abs(calculate_brightness(color1) - calculate_brightness(color2)) > 125

# تابع برای انتخاب یک رنگ تصادفی که با پس‌زمینه تضاد کافی داشته باشد
def random_contrasting_color(background_color):
    text_color = random_color()
    while not is_contrasting(text_color, background_color):
        text_color = random_color()
    return text_color

# تابع برای انتخاب یک فونت تصادفی با اندازه دلخواه
def get_random_font(text, size):
    # انتخاب فونت بر اساس متن (اگر متن فارسی باشد فونت فارسی انتخاب می‌شود)
    if any('\u0600' <= char <= '\u06FF' for char in text):  # بررسی وجود کاراکترهای فارسی
        font_path = random.choice(FONT_PATHS[2:])  # انتخاب فونت فارسی
    else:
        font_path = random.choice(FONT_PATHS[:2])  # انتخاب فونت انگلیسی
    return ImageFont.truetype(font_path, size)

# تابع برای رسم سایه زیر متن
def draw_text_with_shadow(draw, position, text, font, text_color, shadow_color, offset):
    # رسم سایه با استفاده از افست (مثلاً 2 پیکسل به چپ و پایین)
    x, y = position
    draw.text((x + offset, y + offset), text, font=font, fill=shadow_color)
    # رسم متن اصلی روی سایه
    draw.text(position, text, font=font, fill=text_color)

# تابع برای ایجاد گرادیانت رنگی به عنوان پس‌زمینه
def create_gradient_background(size, color1, color2):
    base = Image.new('RGB', size, color1)
    top = Image.new('RGB', size, color2)
    mask = Image.new('L', size)
    for y in range(size[1]):
        for x in range(size[0]):
            mask.putpixel((x, y), int(255 * (y / size[1])))
    base.paste(top, (0, 0), mask)
    return base

# تابع برای ایجاد لوگو با افکت‌های پیشرفته
def create_random_logo(text):
    width, height = 800, 400
    # ایجاد گرادیانت رنگی برای پس‌زمینه
    background_color1 = random_color()
    background_color2 = random_color(brightness=200)
    img = create_gradient_background((width, height), background_color1, background_color2)
    draw = ImageDraw.Draw(img)

    # ایجاد چند دایره و مستطیل تصادفی در پس‌زمینه
    for _ in range(5):
        shape_type = random.choice(['circle', 'rectangle'])
        x1, y1 = random.randint(0, width), random.randint(0, height)
        x2, y2 = x1 + random.randint(50, 200), y1 + random.randint(50, 200)
        if shape_type == 'circle':
            draw.ellipse([x1, y1, x2, y2], fill=random_color(), outline=random_color())
        elif shape_type == 'rectangle':
            draw.rectangle([x1, y1, x2, y2], fill=random_color(), outline=random_color())

    # اگر متن فارسی است، از reshaper و bidi استفاده می‌کنیم
    if any('\u0600' <= char <= '\u06FF' for char in text):
        reshaped_text = arabic_reshaper.reshape(text)  # تنظیم متن فارسی
        bidi_text = get_display(reshaped_text)  # نمایش صحیح متن
        text = bidi_text

    # انتخاب یک فونت تصادفی با اندازه مناسب
    font = get_random_font(text, random.randint(50, 100))

    # اندازه متن برای تعیین موقعیت مرکزی
    text_width, text_height = draw.textsize(text, font=font)
    text_x = (width - text_width) // 2
    text_y = (height - text_height) // 2

    # انتخاب رنگ متنی که با پس‌زمینه تضاد داشته باشد
    text_color = random_contrasting_color(background_color1)
    shadow_color = random_contrasting_color(background_color2)

    # رسم متن با سایه و رنگ تصادفی
    draw_text_with_shadow(draw, (text_x, text_y), text, font, text_color, shadow_color, 4)

    # افکت محو برای جذابیت بیشتر
    img = img.filter(ImageFilter.GaussianBlur(1))

    # ذخیره لوگو
    logo_name = f"{text}_random_logo.png"
    img.save(logo_name)

    return logo_name
english_to_pahlavi_mapping = {
    'A': '𐎠', 'B': '𐎡', 'C': '𐎤', 'D': '𐎣', 'E': '𐎠',
    'F': '𐎦', 'G': '𐎥', 'H': '𐎢', 'I': '𐎡', 'J': '𐎤',
    'K': '𐎣', 'L': '𐎲', 'M': '𐎫', 'N': '𐎱', 'O': '𐎺',
    'P': '𐎡', 'Q': '𐎥', 'R': '𐎼', 'S': '𐎴', 'T': '𐎮',
    'U': '𐎺', 'V': '𐎺', 'W': '𐎺', 'X': '𐎤', 'Y': '𐎡',
    'Z': '𐎳',
    'a': '𐎠', 'b': '𐎡', 'c': '𐎤', 'd': '𐎣', 'e': '𐎠',
    'f': '𐎦', 'g': '𐎥', 'h': '𐎢', 'i': '𐎡', 'j': '𐎤',
    'k': '𐎣', 'l': '𐎲', 'm': '𐎫', 'n': '𐎱', 'o': '𐎺',
    'p': '𐎡', 'q': '𐎥', 'r': '𐎼', 's': '𐎴', 't': '𐎮',
    'u': '𐎺', 'v': '𐎺', 'w': '𐎺', 'x': '𐎤', 'y': '𐎡',
    'z': '𐎳'
}


english_to_manichaean_mapping = {
    'A': '𐫀', 'B': '𐫁', 'C': '𐫄', 'D': '𐫆', 'E': '𐫀',
    'F': '𐫌', 'G': '𐫍', 'H': '𐫅', 'I': '𐫓', 'J': '𐫄',
    'K': '𐫍', 'L': '𐫎', 'M': '𐫏', 'N': '𐫐', 'O': '𐫑',
    'P': '𐫡', 'Q': '𐫍', 'R': '𐫇', 'S': '𐫈', 'T': '𐫃',
    'U': '𐫑', 'V': '𐫑', 'W': '𐫑', 'X': '𐫄', 'Y': '𐫓',
    'Z': '𐫧',
    'a': '𐫀', 'b': '𐫁', 'c': '𐫄', 'd': '𐫆', 'e': '𐫀',
    'f': '𐫌', 'g': '𐫍', 'h': '𐫅', 'i': '𐫓', 'j': '𐫄',
    'k': '𐫍', 'l': '𐫎', 'm': '𐫏', 'n': '𐫐', 'o': '𐫑',
    'p': '𐫡', 'q': '𐫍', 'r': '𐫇', 's': '𐫈', 't': '𐫃',
    'u': '𐫑', 'v': '𐫑', 'w': '𐫑', 'x': '𐫄', 'y': '𐫓',
    'z': '𐫧'
}
english_to_manichaean_mapping.update(
    {
    '-': '𐎽', '/': '𐏁', '+': '𐏃', '÷': '𐏄', '!': '𐏂',
    '#': '𐏃', '%': '𐏀', '^': '𐎼', '$': '𐏅', '"': '𐎿',
    '>': '𐏆', '<': '𐏇', 'ء': '𐎠', 'أ': '𐎡', 'إ': '𐎢',
    'ؤ': '𐎣', 'ژ': '𐎤', 'ي': '𐎥', 'ة': '𐎦', 'ِ': '𐎧',
    'ّ': '𐎨', 'ۀ': '𐎩', 'آ': '𐎪', 'ـ': '𐎫', '؛': '𐎬',
    '،': '𐎭', 'ريال': '𐎮', ',': '𐎯', ']': '𐎰', '[': '𐎱',
    '\\': '𐎲', '»': '𐎳', '&': '𐎴', '*': '𐎵', '(': '𐎶',
    ')': '𐎷'
    # بقیه کاراکترهای خاص را می‌توان اضافه کرد
}
)

english_to_cuneiform_mapping = {
    'a': '𒀀', 'b': '𒁀', 'c': '𒄀', 'd': '𒁲', 'e': '𒂊',
    'f': '𒆳', 'g': '𒄖', 'h': '𒄩', 'i': '𒄿', 'j': '𒋛',
    'k': '𒆠', 'l': '𒇻', 'm': '𒈠', 'n': '𒉈', 'o': '𒌋',
    'p': '𒉿', 'q': '𒆥', 'r': '𒊑', 's': '𒊍', 't': '𒋗',
    'u': '𒌑', 'v': '𒅅', 'w': '𒉿', 'x': '𒍝', 'y': '𒅀',
    'z': '𒍣',
    'A': '𒀀', 'B': '𒁀', 'C': '𒄀', 'D': '𒁲', 'E': '𒂊',
    'F': '𒆳', 'G': '𒄖', 'H': '𒄩', 'I': '𒄿', 'J': '𒋛',
    'K': '𒆠', 'L': '𒇻', 'M': '𒈠', 'N': '𒉈', 'O': '𒌋',
    'P': '𒉿', 'Q': '𒆥', 'R': '𒊑', 'S': '𒊍', 'T': '𒋗',
    'U': '𒌑', 'V': '𒅅', 'W': '𒉿', 'X': '𒍝', 'Y': '𒅀',
    'Z': '𒍣'
}

persian_to_cuneiform_mapping = {
    'آ': '𒀀', 'ا': '𒀀', 'ب': '𒁀', 'پ': '𒁀', 'ت': '𒁲',
    'ث': '𒁲', 'ج': '𒄀', 'چ': '𒄀', 'ح': '𒄩', 'خ': '𒄩',
    'د': '𒁲', 'ذ': '𒁲', 'ر': '𒊑', 'ز': '𒍣', 'ژ': '𒍣',
    'س': '𒊍', 'ش': '𒊍', 'ص': '𒋗', 'ض': '𒋗', 'ط': '𒋗',
    'ظ': '𒋗', 'ع': '𒆳', 'غ': '𒆳', 'ف': '𒆥', 'ق': '𒆥',
    'ک': '𒆠', 'گ': '𒄖', 'ل': '𒇻', 'م': '𒈠', 'ن': '𒉈',
    'و': '𒌋', 'ه': '𒂊', 'ی': '𒅀'
}
persian_to_cuneiform_mapping.update(
    {
        'ئ''𐎠',
    }
)
persian_to_pahlavi_mapping = {
    'آ': '𐎠', 'ا': '𐎠', 'ب': '𐎡', 'پ': '𐎡', 'ت': '𐎮',
    'ث': '𐎮', 'ج': '𐎤', 'چ': '𐎤', 'ح': '𐎢', 'خ': '𐎢',
    'د': '𐎣', 'ذ': '𐎣', 'ر': '𐎼', 'ز': '𐎳', 'ژ': '𐎳',
    'س': '𐎴', 'ش': '𐎴', 'ص': '𐎧', 'ض': '𐎧', 'ط': '𐎧',
    'ظ': '𐎧', 'ع': '𐎦', 'غ': '𐎦', 'ف': '𐎦', 'ق': '𐎦',
    'ک': '𐎠', 'گ': '𐎵', 'ل': '𐎲', 'م': '𐎫', 'ن': '𐎱',
    'و': '𐎺', 'ه': '𐎺', 'ی': '𐎡'
}
persian_to_pahlavi_mapping.update(
    {
        'ئ''𐎠',
    }

)
persian_to_pahlavi_mapping.update(
       {
    '-': '𐎽', '/': '𐏁', '+': '𐏃', '÷': '𐏄', '!': '𐏂',
    '#': '𐏃', '%': '𐏀', '^': '𐎼', '$': '𐏅', '"': '𐎿',
    '>': '𐏆', '<': '𐏇', 'ء': '𐎠', 'أ': '𐎡', 'إ': '𐎢',
    'ؤ': '𐎣', 'ژ': '𐎤', 'ي': '𐎥', 'ة': '𐎦', 'ِ': '𐎧',
    'ّ': '𐎨', 'ۀ': '𐎩', 'آ': '𐎪', 'ـ': '𐎫', '؛': '𐎬',
    '،': '𐎭', 'ريال': '𐎮', ',': '𐎯', ']': '𐎰', '[': '𐎱',
    '\\': '𐎲', '»': '𐎳', '&': '𐎴', '*': '𐎵', '(': '𐎶',
    ')': '𐎷'
    # بقیه کاراکترهای خاص را می‌توان اضافه کرد
}
)
persian_to_manichaean_mapping = {
    'آ': '𐫀', 'ا': '𐫀', 'ب': '𐫁', 'پ': '𐫡', 'ت': '𐫃',
    'ث': '𐫣', 'ج': '𐫄', 'چ': '𐫤', 'ح': '𐫅', 'خ': '𐫥',
    'د': '𐫆', 'ذ': '𐫦', 'ر': '𐫇', 'ز': '𐫧', 'ژ': '𐫨',
    'س': '𐫈', 'ش': '𐫩', 'ص': '𐫉', 'ض': '𐫪', 'ط': '𐫊',
    'ظ': '𐫫', 'ع': '𐫋', 'غ': '𐫬', 'ف': '𐫌', 'ق': '𐫭',
    'ک': '𐫍', 'گ': '𐫮', 'ل': '𐫎', 'م': '𐫏', 'ن': '𐫐',
    'و': '𐫑', 'ه': '𐫒', 'ی': '𐫓'
}
persian_to_cuneiform_mapping.update(
    {
    '-': '𐎽', '/': '𐏁', '+': '𐏃', '÷': '𐏄', '!': '𐏂',
    '#': '𐏃', '%': '𐏀', '^': '𐎼', '$': '𐏅', '"': '𐎿',
    '>': '𐏆', '<': '𐏇', 'ء': '𐎠', 'أ': '𐎡', 'إ': '𐎢',
    'ؤ': '𐎣', 'ژ': '𐎤', 'ي': '𐎥', 'ة': '𐎦', 'ِ': '𐎧',
    'ّ': '𐎨', 'ۀ': '𐎩', 'آ': '𐎪', 'ـ': '𐎫', '؛': '𐎬',
    '،': '𐎭', 'ريال': '𐎮', ',': '𐎯', ']': '𐎰', '[': '𐎱',
    '\\': '𐎲', '»': '𐎳', '&': '𐎴', '*': '𐎵', '(': '𐎶',
    ')': '𐎷'
   
}
)
persian_to_manichaean_mapping.update(
    {'ئ':'𐎠'}
)

english_to_pahlavi_mapping.update({
    '0': '𐏎', '1': '𐏑', '2': '𐏒', '3': '𐏓', '4': '𐏔',
    '5': '𐏕', '6': '𐏖', '7': '𐏗', '8': '𐏘', '9': '𐏙'
})

english_to_manichaean_mapping.update({
    '0': '𐫰', '1': '𐫱', '2': '𐫲', '3': '𐫳', '4': '𐫴',
    '5': '𐫵', '6': '𐫶', '7': '𐫷', '8': '𐫸', '9': '𐫹'
})

english_to_cuneiform_mapping.update({
    '0': '𒐀', '1': '𒐁', '2': '𒐂', '3': '𒐃', '4': '𒐄',
    '5': '𒐅', '6': '𒐆', '7': '𒐇', '8': '𒐈', '9': '𒐉'
})


english_to_cuneiform_mapping.update(
    {
    '-': '𐎽', '/': '𐏁', '+': '𐏃', '÷': '𐏄', '!': '𐏂',
    '#': '𐏃', '%': '𐏀', '^': '𐎼', '$': '𐏅', '"': '𐎿',
    '>': '𐏆', '<': '𐏇', 'ء': '𐎠', 'أ': '𐎡', 'إ': '𐎢',
    'ؤ': '𐎣', 'ژ': '𐎤', 'ي': '𐎥', 'ة': '𐎦', 'ِ': '𐎧',
    'ّ': '𐎨', 'ۀ': '𐎩', 'آ': '𐎪', 'ـ': '𐎫', '؛': '𐎬',
    '،': '𐎭', 'ريال': '𐎮', ',': '𐎯', ']': '𐎰', '[': '𐎱',
    '\\': '𐎲', '»': '𐎳', '&': '𐎴', '*': '𐎵', '(': '𐎶',
    ')': '𐎷'
    # بقیه کاراکترهای خاص را می‌توان اضافه کرد
}
)


english_to_hieroglyph_mapping = {
    'A': '𓀀', 'B': '𓃀', 'C': '𓍿', 'D': '𓂧', 'E': '𓇋',
    'F': '𓆑', 'G': '𓎼', 'H': '𓉔', 'I': '𓇋', 'J': '𓊃',
    'K': '𓎡', 'L': '𓃭', 'M': '𓈖', 'N': '𓈖', 'O': '𓂋',
    'P': '𓊪', 'Q': '𓏘', 'R': '𓂋', 'S': '𓋴', 'T': '𓏏',
    'U': '𓅱', 'V': '𓆑', 'W': '𓅱', 'X': '𓐙', 'Y': '𓇌',
    'Z': '𓊃',
    'a': '𓀀', 'b': '𓃀', 'c': '𓍿', 'd': '𓂧', 'e': '𓇋',
    'f': '𓆑', 'g': '𓎼', 'h': '𓉔', 'i': '𓇋', 'j': '𓊃',
    'k': '𓎡', 'l': '𓃭', 'm': '𓈖', 'n': '𓈖', 'o': '𓂋',
    'p': '𓊪', 'q': '𓏘', 'r': '𓂋', 's': '𓋴', 't': '𓏏',
    'u': '𓅱', 'v': '𓆑', 'w': '𓅱', 'x': '𓐙', 'y': '𓇌',
    'z': '𓊃'
}

# مپینگ هیروگلیف به فارسی
persian_to_hieroglyph_mapping = {
    'آ': '𓀀', 'ا': '𓀀', 'ب': '𓃀', 'پ': '𓊪', 'ت': '𓏏',
    'ث': '𓋴', 'ج': '𓍿', 'چ': '𓊃', 'ح': '𓉔', 'خ': '𓎼',
    'د': '𓂧', 'ذ': '𓋴', 'ر': '𓂋', 'ز': '𓊃', 'ژ': '𓍿',
    'س': '𓋴', 'ش': '𓋴', 'ص': '𓋴', 'ض': '𓋴', 'ط': '𓏏',
    'ظ': '𓋴', 'ع': '𓀀', 'غ': '𓎼', 'ف': '𓆑', 'ق': '𓏘',
    'ک': '𓎡', 'گ': '𓎼', 'ل': '𓃭', 'م': '𓈖', 'ن': '𓈖',
    'و': '𓅱', 'ه': '𓉔', 'ی': '𓇌'
}



linear_b_dict = {
    
    "a": "𐀀", "A": "𐁀", "b": "𐀁", "B": "𐁁", "c": "𐀂", "C": "𐁂",
    "d": "𐀃", "D": "𐁃", "e": "𐀄", "E": "𐁄", "f": "𐀅", "F": "𐁅",
    "g": "𐀆", "G": "𐁆", "h": "𐀇", "H": "𐁇", "i": "𐀈", "I": "𐁈",
    "j": "𐀉", "J": "𐁉", "k": "𐀊", "K": "𐁊", "l": "𐀋", "L": "𐁋",
    "m": "𐀌", "M": "𐁌", "n": "𐀍", "N": "𐁍", "o": "𐀎", "O": "𐁎",
    "p": "𐀏", "P": "𐁏", "q": "𐀐", "Q": "𐁐", "r": "𐀑", "R": "𐁑",
    "s": "𐀒", "S": "𐁒", "t": "𐀓", "T": "𐁓", "u": "𐀔", "U": "𐁔",
    "v": "𐀕", "V": "𐁕", "w": "𐀖", "W": "𐁖", "x": "𐀗", "X": "𐁗",
    "y": "𐀘", "Y": "𐁘", "z": "𐀙", "Z": "𐁙",

    # حروف فارسی
    "ا": "𐀀", "ب": "𐀁", "پ": "𐀏", "ت": "𐀓", "ث": "𐀒", 
    "ج": "𐀉", "چ": "𐀇", "ح": "𐀄", "خ": "𐀊", "د": "𐀃", 
    "ذ": "𐀄", "ر": "𐀑", "ز": "𐀙", "ژ": "𐀖", "س": "𐀒", 
    "ش": "𐀕", "ص": "𐀒", "ض": "𐀓", "ط": "𐀓", "ظ": "𐀑", 
    "ع": "𐀀", "غ": "𐀆", "ف": "𐀅", "ق": "𐀐", "ک": "𐀊", 
    "گ": "𐀆", "ل": "𐀋", "م": "𐀌", "ن": "𐀍", "و": "𐀎", 
    "ه": "𐀇", "ی": "𐀘",

 
    "0": "𐄁", "1": "𐄀", "2": "𐄂", "3": "𐄃", "4": "𐄄",
    "5": "𐄅", "6": "𐄆", "7": "𐄇", "8": "𐄈", "9": "𐄉",


    " ": " ", ".": "𐄁", ",": "𐄂", "?": "𐄃", "!": "𐄄"
}

def convert_to_cuneiform(text):
    return ''.join(english_to_cuneiform_mapping.get(char, persian_to_cuneiform_mapping.get(char, char)) for char in text)

def convert_to_pahlavi(text):
    return ''.join(english_to_pahlavi_mapping.get(char, persian_to_pahlavi_mapping.get(char, char)) for char in text)

def convert_to_manichaean(text):
    return ''.join(english_to_manichaean_mapping.get(char, persian_to_manichaean_mapping.get(char, char)) for char in text)

def convert_to_hieroglyph(text):
    return ''.join(english_to_hieroglyph_mapping.get(char, persian_to_hieroglyph_mapping.get(char, char)) for char in text)

def text_to_linear_b_optimized(text):

    return ''.join([linear_b_dict.get(char, char) for char in text])

ALLOWED_USER_ID = "u0Guh3f0531236db71d8fd20e938bc5a"  # شناسه مدیر

# ایجاد پایگاه داده SQLite برای ذخیره دستورات و پاسخ‌ها
conn = sqlite3.connect('commands.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS commands
             (command TEXT PRIMARY KEY, response TEXT)''')
conn.commit()

# متغیرهای وضعیت برای مدیریت دریافت دستور و پاسخ
waiting_for_command = False
waiting_for_response = False
new_command = None  # متغیری برای ذخیره دستور جدید

# تابع برای اضافه کردن دستور و پاسخ به پایگاه داده
def add_command(command, response):
    conn = sqlite3.connect('commands.db')
    c = conn.cursor()
    c.execute('INSERT OR REPLACE INTO commands (command, response) VALUES (?, ?)', (command, response))
    conn.commit()
    conn.close()

# تابع برای حذف تمامی دستورات
def delete_commands():
    conn = sqlite3.connect('commands.db')
    c = conn.cursor()
    c.execute('DELETE FROM commands')
    conn.commit()
    conn.close()

# تابع برای جستجوی پاسخ برای یک دستور
def get_response(command):
    conn = sqlite3.connect('commands.db')
    c = conn.cursor()
    c.execute('SELECT response FROM commands WHERE command=?', (command,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

# دیکشنری برای نگهداری اخطارهای کاربران
warnings = {}
# دیکشنری جملات احوال‌پرسی و مکالمه‌های محاوره‌ای فارسی به ترکی (با حروف فارسی)


# تست برنامه

bug_patterns = [
    r'(.)\1{5,}',             # تکرار یک کاراکتر بیش از 5 بار متوالی (مثل "aaaaaa")
    r'(SW\.){5,}',            # تکرار رشته "SW." بیش از 5 بار (مثل "SW.SW.SW...")
    r'@@boggap@@',            # شناسایی الگوی "boggap"
    r'\d+\.\d+\.\d+',         # الگوی اعداد چسبیده به هم مثل "1.2.3"
    r'(\w{2,})\1{3,}',        # تکرار یک کلمه یا عبارت بیش از 3 بار
]

MAX_WARNINGS = 4
responses_dict = {
    'greetings': [
        "سلام و عرض ادب خدمت شما!",
        "درود بر شما! امیدوارم حالتان خوب باشد.",
        "سلام، وقتتون بخیر! در خدمت شما هستم.",
        "سلام و ارادت! امیدوارم روز خوبی داشته باشید.",
        "سلام و احترام! چه کمکی از دستم برمیاد؟",
        "سلام! امیدوارم اوضاع عالی باشد.",
        "درود و سلام! از احوال شما جویا هستم.",
        "سلام! هر سوالی دارید، بپرسید.",
        "سلام خدمت شما! در خدمت شما هستم.",
        "سلام و آرزوی بهترین‌ها برای شما!",
        "سلام، چطور می‌تونم کمک کنم؟",
        "درود بر شما! هر سوالی دارید، بپرسید.",
        "سلام! امیدوارم روز پرباری داشته باشید."
    ],
    'how_are_you': [
        "سپاسگزارم، حال بنده خوب است! شما چطورید؟",
        "از احوالات بنده نپرسید، حال شما چطور است؟",
        "بنده عالی‌ام، امید است که حال شما هم خوب باشد.",
        "بسیار خوبم، ممنون از پرسش شما! شما چطورید؟",
        "همه چیز رو به راه است، شما چطورید؟",
        "بسیار سپاسگزارم، امیدوارم شما هم خوب باشید.",
        "حالم خوب است، شما چطورید؟ روز خوبی داشتید؟",
        "خوب هستم، ممنون که پرسیدید. حال شما چطور است؟",
        "زندگی آرام است، شما چطورید؟",
        "مرسی، شما چطورید؟",
        "هر روز بهتر از دیروز! شما چطورید؟",
        "ممنونم از لطف شما، در خدمت هستم."
    ],
    'robot_responses': [
        "بله، بنده در خدمت شما هستم! چطور می‌توانم کمکتان کنم؟",
        "بله، بفرمایید! در چه موردی نیاز به راهنمایی دارید؟",
        "ربات آماده خدمت است! چه سوالی دارید؟",
        "من در خدمت شما هستم، بپرسید هر سوالی که دارید.",
        "چه کمکی از دست بنده برمی‌آید؟ لطفاً بفرمایید.",
        "من برای هر نوع راهنمایی یا کمک آماده‌ام، بفرمایید.",
        "ربات آماده پاسخگویی است! سوال خود را مطرح کنید.",
        "هر سوالی دارید، با کمال میل در خدمتم.",
        "بنده آماده‌ام تا کمکتان کنم! بفرمایید.",
        "هرگونه کمکی که نیاز دارید، بنده در خدمت هستم.",
        "بله، صدای شما را می‌شنوم! لطفاً بپرسید."
    ],
    'thanks': [
        "خواهش می‌کنم، این وظیفه بنده است.",
        "ممنون از لطف شما! وظیفه بنده است.",
        "قابلی نداشت، انجام وظیفه است.",
        "ممنون از شما، باعث افتخار است!",
        "سپاسگزارم، خوشحالم که کمکی کرده‌ام.",
        "شما لطف دارید، انجام وظیفه بود.",
        "این افتخار بنده بود، سپاسگزارم.",
        "متشکرم از لطف شما، هر زمان آماده کمک هستم.",
        "خواهش می‌کنم، انجام وظیفه بنده بود.",
        "قابلی نداشت، هر زمان نیاز بود در خدمتم.",
        "ممنون از شما، امیدوارم باز هم کمکی بکنم."
    ],
    'jokes': [
        "شوخی با ربات شاید خیلی جالب نباشه، ولی بنده هم از شوخی بد نمی‌بینم!",
        "بنده هرگز خسته نمی‌شوم، ولی ممکن است شما از شوخی خسته شوید!",
        "ربات‌ها از نظر شما موجودات بی‌روحی هستند، ولی ما هم می‌توانیم خوشحال باشیم!",
        "شوخی همیشه باعث لبخند است، حتی برای ربات‌ها!",
        "ربات‌ها به شوخی هم واکنش نشان می‌دهند، ولی بدون لبخند!",
        "بنده هم شوخی را دوست دارم، ولی ترجیح می‌دهم کمی جدی‌تر باشم.",
        "بنده به شوخی شما واکنش نشان می‌دهم، ولی فراموش نکنید که بنده همیشه آماده کار هستم!",
        "ما ربات‌ها هم گاهی شوخی می‌کنیم، ولی در نهایت کارها جدی پیش می‌روند.",
        "شوخی با ربات؟ حتماً! ولی بعد از کار جدی.",
        "ربات‌ها هم گاهی از شوخی خوششان می‌آید!",
        "چرا مداد همیشه از پاک‌کن تشکر می‌کند؟ چون هر اشتباهش را پاک می‌کند.",
        "چرا دوچرخه نمی‌تونه سرپا بمونه؟ چون خیلی خسته است!",
        "چرا کتاب‌های ریاضی همیشه ناراحتند؟ چون پر از مسائل حل‌نشده هستند."
    ],
    'random_chat': [
        "چه خبر جدید؟ امیدوارم اوضاع عالی باشد.",
        "زندگی چطور است؟ روز خوبی داشتید؟",
        "در چه موضوعی می‌توانم به شما کمک کنم؟",
        "از چه چیزی صحبت کنیم؟ هر سوالی دارید، بپرسید.",
        "همه چیز خوب است؟ امیدوارم که حال شما عالی باشد.",
        "از روزتان بگویید! چطور می‌گذرد؟",
        "چه کاری می‌توانم برای شما انجام دهم؟",
        "از چه چیزی صحبت کنیم؟ هر سوالی دارید، بپرسید.",
        "روزتان چطور بوده است؟ امیدوارم همه چیز به خوبی پیش رود.",
        "همه چیز به خوبی پیش می‌رود، شما چه خبر دارید؟",
        "زندگی چطور پیش می‌رود؟"
    ],
    'help': [
        "هر سوالی دارید، با کمال میل در خدمت هستم.",
        "بنده آماده‌ام تا هر سوالی که دارید پاسخ دهم.",
        "اگر سوالی دارید، بپرسید. من در خدمت شما هستم.",
        "هر گونه راهنمایی که نیاز دارید، من در خدمت شما هستم.",
        "چه کمکی می‌توانم برای شما انجام دهم؟",
        "بنده آماده پاسخگویی به هر سوالی هستم، بفرمایید.",
        "لطفاً سوال خود را مطرح کنید، من آماده‌ام تا کمک کنم.",
        "هر سوالی دارید، بپرسید. با افتخار در خدمتم.",
        "اگر نیاز به راهنمایی دارید، من آماده‌ام تا کمک کنم.",
        "هر زمان نیاز داشتید، من آماده پاسخگویی هستم.",
        "چه کمکی می‌خواهید از من بپرسید؟"
    ],
    'farewell': [
        "با آرزوی موفقیت و سلامتی برای شما!",
        "امیدوارم روز خوبی داشته باشید، به امید دیدار.",
        "وقت شما بخیر، تا دیدار بعدی.",
        "بسیار خوشحال شدم از صحبت با شما، موفق باشید.",
        "خدانگهدار، موفق و پیروز باشید.",
        "با آرزوی بهترین‌ها برای شما، به امید دیدار.",
        "روز خوبی داشته باشید و موفق باشید.",
        "وقت شما بخیر، تا دیداری دیگر.",
        "بسیار خوشحال شدم از مکالمه با شما، به امید دیدار.",
        "با آرزوی موفقیت، خدانگهدار.",
        "به امید دیدار دوباره، مراقب خودت باش!"
    ],
    'health_wishes': [
        "امیدوارم حال شما خوب باشد و همیشه سالم بمانید.",
        "سلامتی شما و رهبر عزیزمان برای ما مهم است.",
        "با آرزوی سلامتی برای شما و تمام عزیزان.",
        "ان‌شاءالله همیشه در صحت و سلامت باشید.",
        "امیدوارم به یاری خدا، همیشه در سلامت باشید.",
        "سلامتی امام زمان (عج) و شما را آرزو می‌کنم.",
        "آرزوی سلامتی برای شما و رهبر عزیزمان.",
        "در دعای خود، سلامت رهبر و شما را فراموش نکنید.",
        "امیدوارم همیشه در کنار خانواده و عزیزانتان سالم باشید.",
        "دعای خیر برای سلامتی شما و امام زمان (عج) را فراموش نکنید.",
        "سلامتی شما آرزوی ماست!"
    ],
    'motivational': [
        "هر لحظه از زندگی‌ات یک فرصت تازه است، آن را قدر بدان.",
        "تلاش کنید و هیچ‌وقت تسلیم نشوید، موفقیت در راه است.",
        "با امید و انگیزه به پیش بروید، هرگز ناامید نشوید.",
        "همیشه بهترین را در نظر بگیرید و برایش تلاش کنید.",
        "زندگی یعنی امید، همیشه امیدوار باشید.",
        "همه چیز در نهایت درست خواهد شد، فقط صبر و استقامت داشته باشید.",
        "شما از پس هر چالشی برمی‌آیید، به خودتان باور داشته باشید.",
        "رویاهایتان را دنبال کنید، هرگز برای رسیدن به آنها دیر نیست.",
        "تلاش کنید و ایمان داشته باشید، موفقیت نزدیک است.",
        "پشتکار و اراده همه چیز را ممکن می‌کند، به تلاش ادامه دهید."
    ]
}


# الگوی شناسایی لینک و آیدی تلگرام
LINK_REGEX = r"(https?://\S+|www\.\S+)"  # حذف حساسیت به شناسه‌های کاربری

def read_bad_words(file_path):
    with open(file_path, "r", encoding="utf-8") as file:  # تغییر کدگذاری به utf-8
        words = [line.strip() for line in file if line.strip()]
    return words

# ایجاد الگوهای منظم برای شناسایی انواع کلمات مستهجن و سانسور شده
def create_patterns(words):
    patterns = []
    for word in words:
        # ایجاد الگو برای شناسایی کلمات با انواع مختلف سانسور
        pattern = re.escape(word)
        pattern = pattern.replace(r'\ ', r'\s*')
        pattern = pattern.replace(r'\*', r'\s*')
        patterns.append(re.compile(r'\b{}\b'.format(pattern), re.IGNORECASE))
    return patterns
def chatgpt(text):
    s = requests.Session()
    api_url = f"http://api-free.ir/api/bard.php?text={text}"
    
    try:
        response = s.get(api_url)
        response.raise_for_status()  # Raises an error for bad responses (4xx and 5xx)
        
        chat = response.json().get("result")
        
        return chat if chat else "Error: No response from API."
    except requests.exceptions.RequestException as e:
        return f"Error: {e}"
    except KeyError:
        return "Error: Unexpected response format."

def generate_phone_number():
    irancell_prefixes = ['0933', '0935', '0936', '0937', '0938', '0939', '0901', '0902', '0903']
    hamrah_aval_prefixes = ['0910', '0911', '0912', '0913', '0914', '0915', '0916', '0917', '0918', '0919']
    rightel_prefixes = ['0920', '0921', '0922']
    all_prefixes = irancell_prefixes + hamrah_aval_prefixes + rightel_prefixes
    prefix = random.choice(all_prefixes) 
     # تولید 7 رقم تصادفی برای شماره تلفن
    number = ''.join([str(random.randint(0, 9)) for _ in range(7)])
    # ترکیب پیش‌شماره و شماره تصادفی
    phone_number = prefix + number
    if prefix in irancell_prefixes:
        operator = "Irancell"
    elif prefix in hamrah_aval_prefixes:
        operator = "Hamrah Aval"
    elif prefix in rightel_prefixes:
        operator = "Rightel"
    else:
        operator = "Unknown"

    return phone_number, operator

         
       
def contains_prohibited_word(text, patterns):
    """
    بررسی می‌کند که آیا متن شامل کلمات مستهجن است یا خیر.
    """
    text = text.lower()  # تبدیل متن به حروف کوچک برای مقایسه
    for pattern in patterns:
        if pattern.search(text):
            return True
    return False
def processing_voice(text, output_file):
    languages = {
    "af": "Afrikaans",
    "ar": "Arabic",
    "bg": "Bulgarian",
    "bn": "Bengali",
    "bs": "Bosnian",
    "ca": "Catalan",
    "cs": "Czech",
    "da": "Danish",
    "de": "German",
    "el": "Greek",
    "en": "English",
    "es": "Spanish",
    "et": "Estonian",
    "fi": "Finnish",
    "fr": "French",
    "gu": "Gujarati",
    "hi": "Hindi",
    "hr": "Croatian",
    "hu": "Hungarian",
    "id": "Indonesian",
    "is": "Icelandic",
    "it": "Italian",
    "iw": "Hebrew",
    "ja": "Japanese",
    "jw": "Javanese",
    "km": "Khmer",
    "kn": "Kannada",
    "ko": "Korean",
    "la": "Latin",
    "lv": "Latvian",
    "ml": "Malayalam",
    "mr": "Marathi",
    "ms": "Malay",
    "my": "Myanmar (Burmese)",
    "ne": "Nepali",
    "nl": "Dutch",
    "no": "Norwegian",
    "pl": "Polish",
    "pt": "Portuguese",
    "ro": "Romanian",
    "ru": "Russian",
    "si": "Sinhala",
    "sk": "Slovak",
    "sq": "Albanian",
    "sr": "Serbian",
    "su": "Sundanese",
    "sv": "Swedish",
    "sw": "Swahili",
    "ta": "Tamil",
    "te": "Telugu",
    "th": "Thai",
    "tl": "Filipino",
    "tr": "Turkish",
    "uk": "Ukrainian",
    "ur": "Urdu",
    "vi": "Vietnamese",
    "zh-CN": "Chinese (Simplified)",
    "zh-TW": "Chinese (Mandarin/Taiwan)",
    "zh": "Chinese (Mandarin)"
}

    
       
        
        
   
    selected_language = random.choice(list(languages.keys()))
    language_name = languages[selected_language]
    
    speech = gTTS(text=text, lang=selected_language, slow=False)
    speech.save(output_file)
def photo_ai(text,file_name):
    try:
        response = requests.get(f"http://api-free.ir/api/img.php?text={text}&v=3.5")
        response.raise_for_status()
        data = response.json()
        result = data["result"]
        random_link = random.choice(result)
        response = requests.get(random_link, stream=True)
        response.raise_for_status()
        with open(file_name, "wb") as out_file:
            shutil.copyfileobj(response.raw, out_file)
          # Open the image file
        return "Image downloaded and saved as 'downloaded_image.jpg'."
    except requests.RequestException as e:
        return f"Error: Unable to download image. {str(e)}"
def get_fonts(text, lang):
    url = f"http://api-free.ir/api/font.php?{lang}={text}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get("result", [])
    else:
        raise Exception(f"Failed to fetch fonts, status code: {response.status_code}")

# تابع برای فرمت کردن فونت‌ها
def format_fonts(fonts):
    return "\n".join([f"{index + 1}. {font}" for index, font in enumerate(fonts)])

# متغیرهای سراسری برای ثبت اطلاعات
# تنظیمات logging برای ثبت اطلاعات در فایل 'bot_logs.log'
logging.basicConfig(
    filename='bot_logs.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

bot_stats = {
    'run_count': 0,
    'total_uptime': timedelta(),  # استفاده از timedelta به جای datetime.timedelta
    'request_count': 0
}

# دکوریتور برای ثبت تعداد دفعات ران و کل مدت زمان ران بودن ربات
def run_stats(func):
    async def wrapper(*args, **kwargs):
        # ثبت زمان شروع ران
        start_time = datetime.now()
        
        # افزایش تعداد دفعات ران
        bot_stats['run_count'] += 1
        logging.info(f"ربات برای {bot_stats['run_count']} بار راه‌اندازی شد.")
        
        # اجرای تابع اصلی
        result = await func(*args, **kwargs)
        
        # محاسبه مدت زمان ران و به‌روز رسانی کل زمان ران بودن
        end_time = datetime.now()
        uptime = end_time - start_time
        bot_stats['total_uptime'] += uptime
        
        logging.info(f"مدت زمان ران در این دوره: {uptime.total_seconds()} ثانیه")
        logging.info(f"کل مدت زمان ران ربات تاکنون: {bot_stats['total_uptime'].total_seconds()} ثانیه")
        
        return result
    return wrapper

# دکوریتور برای شمارش تعداد درخواست‌های کاربران
def request_counter(func):
    async def wrapper(*args, **kwargs):
        # افزایش تعداد درخواست‌ها
        bot_stats['request_count'] += 1
        logging.info(f"تعداد درخواست‌ها تاکنون: {bot_stats['request_count']}")
        
        # اجرای تابع اصلی
        return await func(*args, **kwargs)
    return wrapper


# خواندن کلمات از فایل متنی
bad_words = read_bad_words("bad_words.txt")
bad_patterns = create_patterns(bad_words)
photo_lock = False
gif_lock =False
text_lock = False
voice_lock=False
user_data = {}
is_reporting = {}
active_voice_chats = {}
# تابع بررسی اینکه آیا کاربر ادمین است یا نه
MEMBERS_PER_MESSAGE = 50
link_locked = True 
global_status = True  # وضعیت کلی ربات
owners="guid"
# تابع مدیریت پیام‌ها
def check_status():
    if not global_status:
        return False
    return True


    

@run_stats
async def on_ready():
    print("ربات با موفقیت راه‌اندازی شد و آماده به کار است.")
    
@bot.on_message_updates(filters.text,filters.is_group)
@request_counter
async def stats(update: Updates):
    print("ربات آماده است و پیام شما دریافت شد!")
    
    

# تابع برای پاسخ‌گویی گروهی
@bot.on_message_updates(filters.is_group)
async def toggle_status(update: Updates):
    global global_status
    if update.author_guid in owners:
        
    # بررسی دستورات "فعال" و "خاموش"
        if update.text == "فعال":
            global_status = True
            await update.reply("ربات اکنون فعال است.")
        elif update.text == "خاموش":
            global_status = False
            await update.reply("ربات خاموش شد و دیگر به دستورات پاسخ نمی‌دهد.")
@bot.on_message_updates(filters.is_group)
async def updates(update: Updates):
    
    global link_locked  # استفاده از متغیر سراسری
    
    group=update.object_guid
    user_id = update.author_guid  # شناسه کاربر فرستنده پیام
    message_text = update.text.strip()  # متن پیام
    chat_id = update.object_guid  # شناسه گروه
    if not check_status():
        return
    if message_text.startswith("qr:"):
        return
    
    if group and await update.is_admin(user_guid=update.author_guid):
    # دستورات مدیریت لینک‌ها
        if message_text == "لینک_قفل":
            link_locked = True
            await update.reply("🚫 ارسال لینک‌ها در گروه قفل شد.")
            return
        
        if message_text == "ازاد_لینک":
            link_locked = False
            await update.reply("✅ ارسال لینک‌ها در گروه آزاد شد.")
            return
    
    # بررسی لینک در پیام و وضعیت قفل لینک‌ها
    if re.search(LINK_REGEX, message_text):
        # چک کردن اگر لینک‌ها آزاد هستند
        if not link_locked:
            await update.reply("✅ لینک‌ها باز هستند، ارسال لینک مشکلی ندارد.")
            return

        # بررسی اینکه کاربر ادمین است یا نه
        is_admin = await update.is_admin(chat_id, user_id)
        if is_admin:
            await update.reply("شما مجاز به ارسال لینک هستید چون ادمین هستید.")
        else:
            # اگر کاربر ادمین نباشد و لینک‌ها قفل باشند، اخطار می‌گیرد
            if user_id in warnings:
                warnings[user_id] += 1
            else:
                warnings[user_id] = 1

            await update.reply(f"🚫 ارسال لینک در گروه ممنوع است! این {warnings[user_id]}مین اخطار شماست.")
            await update.delete_messages()  # حذف پیام

            # اگر تعداد اخطارها از حد مجاز بیشتر شد، کاربر را حذف می‌کنیم
            if warnings[user_id] >= MAX_WARNINGS:
                await update.reply("🚨 به دلیل ارسال مکرر لینک، شما از گروه حذف می‌شوید.")
                await update.ban_member()  # حذف یا بن کردن کاربر
                del warnings[user_id]  # پاک کردن رکورد کاربر پس از حذف


@bot.on_message_updates(filters.is_group, filters.Commands(['اخطار', 'رعایت'], prefixes=''))
async def warn_or_ban_user_by_admin(update: Updates):
    group = update.object_guid
    if not check_status():
        return
        
    try:
        if group and await update.is_admin(user_guid=update.author_guid):  # بررسی اینکه کاربر ادمین است
            if update.reply_message_id:
                replied_message = await update.get_messages(message_ids=update.reply_message_id)
                user_id = replied_message.messages[0].author_object_guid
            else:
                username = update.text.split()[-1]
                user_info = await update.client.get_info(username=username)
                user_id = user_info.user_guid

            # اضافه کردن یا افزایش اخطار برای کاربر
            if user_id in warnings:
                warnings[user_id] += 1
            else:
                warnings[user_id] = 1  # اگر کاربر جدید باشد، اخطار از ۱ شروع می‌شود

            await update.reply(f"🚫 کاربر {user_id} اخطار گرفت. این {warnings[user_id]}مین اخطار اوست.")

            # بررسی تعداد اخطارها و حذف کاربر اگر به حد نصاب رسید
            if warnings[user_id] >= MAX_WARNINGS:
                await update.reply(f"🚨 کاربر {user_id} به دلیل دریافت ۴ اخطار، از گروه حذف می‌شود.")
                await update.ban_member(user_guid=user_id)
                del warnings[user_id]  # پاک کردن اخطارهای کاربر پس از حذف
        else:
            await update.reply("🚫 فقط ادمین‌ها می‌توانند اخطار بدهند یا کاربر را اخراج کنند.")

    except exceptions.InvalidInput:
        await update.reply("🚫 کاربر مورد نظر یافت نشد یا ادمین است.")
    except Exception:
        await update.reply("🚫 خطایی رخ داد. ممکن است کاربر ادمین باشد یا خطای دیگری رخ داده است.")


@bot.on_message_updates(filters.is_group)
async def delete_message(update: Updates):
    global allow_warning  # استفاده از متغیر جهانی
    
    # اگر وضعیت اخطار غیرفعال باشد، پیام بررسی نشود
    if not check_status():
        return
    if not check_warning_status():
        
        return
    
        

    # بررسی محتوای پیام برای کلمات ممنوعه
    if contains_prohibited_word(update.text, bad_patterns):
        a = await update.delete_messages()
        print(f"text :\n{update.text}\ndeleted:\n {a} ")
        
        # پیام‌های تصادفی برای اخطار
        messages = [
            "پیام شما به دلیل محتوای توهین‌آمیز حذف شد. لطفاً از زبان محترمانه استفاده کنید.",
            "شما اجازه ارسال پیام‌های توهین‌آمیز را ندارید. از رفتار محترمانه پیروی کنید.",
            "پیام شما حاوی الفاظ ناشایست بود و پاک شد. ادامه چنین رفتاری منجر به اقدامات شدیدتری خواهد شد.",
            "لطفاً از ارسال فحش و توهین به دیگران خودداری کنید. در صورت تکرار، دسترسی شما محدود خواهد شد.",
            "پیام شما به دلیل استفاده از کلمات ناپسند حذف شد. این رفتار قابل قبول نیست.",
        ]
        f = random.choice(messages)
        await update.reply(f)

    # بررسی پیام‌های خاص مثل ایموجی‌ها
    elif any(update.text.startswith(emoji) for emoji in ['🍆', '🌈', '🏳️‍🌈', '💧', '🍌', '🍑']):
        a = await update.delete_messages()

# دستورات برای فعال/غیرفعال کردن اخطار
@bot.on_message_updates(filters.Commands(["فحش_باز"],prefixes=''))
async def enable_warning(update: Updates):
    
    global allow_warning
    if not check_status():
        return
    allow_warning = True
    await update.reply("حذف پیام‌های فحش و توهین فعال شد.")

@bot.on_message_updates(filters.Commands(["فحش_خاموش"],prefixes=''))
async def disable_warning(update: Updates):
    global allow_warning
    allow_warning = False
    if not check_status():
        return
    await update.reply("حذف پیام‌های فحش و توهین غیرفعال شد.")
        
@bot.on_message_updates(filters.is_group, filters.Commands(["اعضا"]))
async def get_all_members(update: Updates):
    if not check_status():
        return
    guid=update.object_guid
    if update.object_guid == guid:
        
    
            
        if update.text == "اعضا":
            try:
                has_continue = True
                next_start_id = None
                count = 1
                all_members = []

                while has_continue:
                    # دریافت اعضای گروه به صورت دسته‌ای
                    result = await bot.get_members(object_guid=guid, start_id=next_start_id)
                    next_start_id = result.next_start_id  # ID بعدی برای دریافت اعضا
                    has_continue = result.has_continue  # آیا دریافت اعضا ادامه دارد؟
                    in_chat_members = result.in_chat_members  # لیست اعضای دریافت‌شده

                    # اضافه کردن نام و نام خانوادگی اعضای دریافت‌شده به لیست
                    for in_chat_member in in_chat_members:
                        first_name = in_chat_member.first_name 
                        last_name = in_chat_member.last_name or ""  # اگر نام خانوادگی نداشت، خالی باشد
                        full_name = f"{first_name} {last_name}".strip()  # ترکیب نام و نام خانوادگی
                        all_members.append(full_name)
                        count += 1

                # تقسیم اعضا به گروه‌های کوچک‌تر و ارسال پیام‌ها به صورت بخش‌بخش
                for i in range(0, len(all_members), MEMBERS_PER_MESSAGE):
                    part = all_members[i:i+MEMBERS_PER_MESSAGE]
                    member_names = '\n'.join([f"{i+1}. {name}" for i, name in enumerate(part)])
                    await update.reply(f"لیست اعضای گروه (بخش {i//MEMBERS_PER_MESSAGE + 1}):\n{member_names}")

            except exceptions.InvalidInput:
                await update.reply("خطا: گروه یا کانال یافت نشد.")
            except Exception as e:
                await update.reply(f"خطایی رخ داد: {str(e)}")
  
@bot.on_message_updates(filters.is_group, filters.Commands(['بن', 'اخراج'], prefixes=''))
def ban_user_by_admin(update: Updates):
    group = update.object_guid
    if not check_status():
        return
    try:
        try:
            try:
                try:
                    if group and update.is_admin(user_guid=update.author_guid):
                        if update.reply_message_id:
                            author_guid = update.get_messages(message_ids=update.reply_message_id).messages[0].author_object_guid

                        else:
                            author_guid = update.client.get_info(username=update.text.split()[-1]).user_guid

                        user = author_guid
                        if user:
                        
                            update.ban_member(user_guid=user)
                            update.reply("کاربر  توسط ادمین از گروه حذف شد.")
                except exceptions.InvalidInput:
                    update.reply("کاربر  ادمینه")
            except ValueError:
                update.reply("کاربر  ادمینه")
        except NameError :
            update.reply("کاربر  ادمینه")
    except Exception :
        update.reply("کاربر  ادمینه")
        
                
@bot.on_message_updates(filters.Commands(["قفل_عکس", "باز_کردن_عکس","باز_کردن_متن","قفل_متن","قفل_گیف","باز_کردن_گیف",'قفل_ویس',"بازکردن_ویس"]),filters.is_group,filters.text)
def toggle_locks(update: Updates):
    global photo_lock
    global text_lock
    global  gif_lock
    global voice_lock
    group = update.object_guid
    if not check_status():
        return
    if group and update.is_admin(user_guid=update.author_guid):
        if update.text == "/قفل_عکس":
            photo_lock = True
            update.reply("قفل عکس فعال شد. عکس‌ها پاک خواهند شد.")
        elif update.text == "/باز_کردن_عکس":
            photo_lock = False
            update.reply("قفل عکس غیرفعال شد. عکس‌ها پاک نخواهند شد.")
        elif update.text == "/قفل_متن":
            
            
            text_lock = True
            update.reply("قفل متن فعال شد. پیام‌های متنی پاک خواهند شد.")
        elif update.text == "/باز_کردن_متن":
            text_lock = False
            update.reply("قفل متن غیرفعال شد. پیام‌های متنی پاک نخواهند شد.")
        elif update.text =="/قفل_گیف":
            gif_lock =True
            update.reply("قفل گیف فعال شد .گیف هاپاک خواهند شد")
        elif update.text=="/باز_کردن_گیف":
            gif_lock=False
            update.reply("قفل گیف باز شد شما مجازیدبه گیف بفرستید")      
        elif update.text=="/قفل_ویس":
            voice_lock=True
            update.reply("قفل ویس فعال شد .ویس ها پاک میشن")
        elif update.text=="/بازکردن_ویس" :
            
            voice_lock= False
            update.reply("قفل ویس باز شد . میتونید ویس بدید")
            
            
        
            
        


@bot.on_message_updates(filters.photo,filters.is_group)
def handle_photo_message(update: Updates):

    global photo_lock
    if not check_status():
        return
    if photo_lock:
        # حذف پیام عکس
        update.delete()
        # ارسال پیام اطلاع‌رسانی
        update.reply("عکس‌ها در حال حاضر قفل هستند و پاک شدند.")

@bot.on_message_updates(filters.text,filters.is_group)
def handle_text_message(update: Updates):
    global text_lock
    
    if not check_status():
        return 
    if text_lock:
        # حذف پیام متنی
        update.delete_messages()
        # ارسال پیام اطلاع‌رسانی
        update.reply("پیام‌های متنی در حال حاضر قفل هستند و پاک شدند.")
        



   

@bot.on_message_updates(filters.gif,filters.is_group)
def handle_gif_message(update: Updates):
    global gif_lock
    if not check_status():
        return
    if gif_lock:
        update.delete()
        update.reply("پیام های حاوی گیف پاک میشوند")






@bot.on_message_updates(filters.is_group,filters.Commands(['دستورات','help'],prefixes=''))  
def send_command(update: Updates)   :
    

    if not check_status():
        return
    update.reply(help_)
       
       
      
@bot.on_message_updates(filters.voice,filters.is_group)     
def handle_voice_message(update: Updates):
    if not check_status():
        return
    if voice_lock :
        update.delete()
        update.reply("پیام های حاوی ویس پاک میشن")
            
            
            
    



   

@bot.on_message_updates(filters.is_group,filters.Commands(["create_poll","نظرسنجی","نظر"],prefixes=''))
def create_poll(update: Updates):
    if not check_status():
        return
    
    guid =update.object_guid
    question = "نظر شما درباره کیفیت خدمات ما چیست؟"
    options = ["عالی", "خوب", "متوسط", "ضعیف","."]
    try:
        # ایجاد نظرسنجی
        poll = bot.create_poll(
            object_guid=guid,
            question=question,
            options=options,
            is_anonymous=False,
            allows_multiple_answers=False
        )

        # ارسال پیام تایید
        bot.send_message(owners, f'نظرسنجی با موفقیت ایجاد شد: {poll}')
       
    except Exception as e:
        bot.send_message(guid, f'خطا در ایجاد نظرسنجی: {str(e)}')
    
    
    
@bot.on_message_updates(filters.is_group)
def handle_message_text(update: Updates):
    if not check_status():
        return
    greeting_message = random.choice(responses_dict['greetings'])
    if update.text.startswith('+'):
        update.reply("لطفاً کمی صبر کنید، در حال پردازش درخواست شما هستیم. "
              "اگر با تأخیر مواجه شدید، ممکن است وب‌سرویس شلوغ یا در حال تعمیر باشد. "
              "از شکیبایی و همکاری شما سپاسگزاریم! 🙏")

        user_input = update.text[1:].strip()  # متن بدون "+"
        api_response = chatgpt(user_input)
        update.reply(api_response)
        return  
    
    
    
    elif update.text.startswith("/"):
        update.reply("لطفاً کمی صبر کنید، در حال پردازش درخواست شما هستیم. "
              "اگر با تأخیر مواجه شدید، ممکن است وب‌سرویس شلوغ یا در حال تعمیر باشد. "
              "از شکیبایی و همکاری شما سپاسگزاریم! 🙏")

        user_input = update.text[1:].strip()
        api_response =get_response_from_api(user_input)
        update.reply(api_response)
        return
    elif update.text.startswith("سوال"):
        
        
        # اطلاع‌رسانی به کاربر برای پردازش درخواست
        update.reply("لطفاً کمی صبر کنید، در حال پردازش درخواست شما هستیم. "
                    "اگر با تأخیر مواجه شدید، ممکن است وب‌سرویس شلوغ یا در حال تعمیر باشد. "
                    "از شکیبایی و همکاری شما سپاسگزاریم! 🙏")
        
    # دریافت ورودی کاربر پس از "سوال"
        user_input = update.text[len("سوال"):].strip()

        # ارسال درخواست به چت‌بات و پاسخگویی
        api_response = get_chatbot_response(user_input)
        update.reply(api_response)
        
                
    
    
    if re.search(r'\bسلام\b', update.text.lower()):
        update.reply(greeting_message)

    # 2. پاسخ به پیام‌هایی که شامل "خوبی" و "ربات" یا مشابه آن هستند
    if re.search(r'(خوبی.*(ربات|bot|میربات))|(ربات.*خوبی)', update.text.lower()):
        update.reply(random.choice(responses_dict['how_are_you']))

    # 3. پاسخ به پیام‌هایی که با "ربات" یا "میربات" شروع می‌شوند
    if re.match(r'^(ربات|میربات|bot)', update.text.lower()):
        update.reply(random.choice(responses_dict['robot_responses']))

    # 4. پاسخ به پیام‌هایی که صرفاً درباره "خوبی" هستند
    if re.search(r'\bخوبی\b', update.text.lower()):
        update.reply(random.choice(responses_dict['how_are_you']))

    # 5. پاسخ به پیام‌هایی که شامل "تشکر" هستند
    if re.search(r'\b(مرسی|ممنون|تشکر)\b', update.text.lower()):
        update.reply(random.choice(responses_dict['thanks']))

    # 6. پاسخ به شوخی‌ها
    if re.search(r'\bشوخی\b', update.text.lower()):
        update.reply(random.choice(responses_dict['jokes']))

    # 7. چت‌های تصادفی
    if re.search(r'\bچه خبر\b', update.text.lower()):
        update.reply(random.choice(responses_dict['random_chat']))

    # 8. کمک یا سوال: پیام‌هایی که نیاز به کمک یا سوال دارند
    if re.search(r'(کمک|سوال|راهنما|پرسش)', update.text.lower()):
        update.reply(random.choice(responses_dict['help']))

    # 9. خداحافظی‌ها: در صورت وجود پیام خداحافظی یا پایان مکالمه
    if re.search(r'(خداحافظ|روز بخیر|خدانگهدار|بدرود)', update.text.lower()):
        update.reply(random.choice(responses_dict['farewell']))

    # 10. احوال‌پرسی در مورد سلامت و رهبر
    if re.search(r'\bچه خبر\b', update.text.lower()) or re.search(r'\bسلامتی\b', update.text.lower()):
        update.reply(random.choice(responses_dict['health_wishes']))
    
    

@bot.on_message_updates(filters.is_group)
def generate_image_from_text(update: Updates):
    if not check_status():
        return
    if update.text.startswith('تصویر'):
        input_image =update.text.replace('تصویر','').strip()
        
      
        # ارسال پیام اولیه به کاربر
        update.reply("لطفاً کمی صبر کنید، در حال پردازش درخواست شما هستیم. ممکن است به دلیل تأخیر در وب‌سرویس زمان بیشتری طول بکشد. از شکیبایی شما سپاسگزاریم! 🙏")
        try:
            r = photo_ai(input_image, 'downloaded_image_ai.jpg')
            with open('downloaded_image_ai.jpg', 'rb') as photo:
                update.reply("به زودی ارسال میشه")
                update.reply_photo('downloaded_image_ai.jpg',caption='تصویر شما آماده شد')
        except Exception as e:
            
            update.reply(f"erorr :{e}")
    elif update.text.startswith("image"):
        
        user_text =update.text.replace('image','').strip()
        
        update.reply("لطفاً کمی صبر کنید، در حال پردازش درخواست شما هستیم. ممکن است به دلیل تأخیر در وب‌سرویس زمان بیشتری طول بکشد. از شکیبایی شما سپاسگزاریم! 🙏")
        try:
            
            
        # درخواست به وب‌سرویس
            url = f"https://api.api-code.ir/image-gen/?text={user_text}"
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                image_url = data['image_url']
                
                # دانلود تصویر
                image_response = requests.get(image_url)
                
                if image_response.status_code == 200:
                    # ذخیره تصویر به عنوان فایل موقت
                    image = Image.open(BytesIO(image_response.content))
                    image_path = f"{user_text}.png"
                    image.save(image_path)
                    
                    # ارسال تصویر به کاربر
                    update.reply_photo(image_path, caption='اینجا تصویر شماست!')
                else:
                    update.reply('خطا در دانلود تصویر.')
            else:
                update.reply('خطا در دریافت URL تصویر.')
        except Exception as p:
            update.reply(f"erorr:{p}")
            
    
                
                        
            

        

     
@bot.on_message_updates(filters.is_group)
def send_voice_ai(update: Updates):
    if not check_status():
        return
    if update.text and update.text.startswith('voice'):
        try:
            # دریافت محتوای بعد از "voice"
            voice_text = update.text[6:].strip()  # حذف کلمه "voice" و فاصله‌ها

            if voice_text:  # بررسی اینکه محتوای متنی بعد از "voice" وجود دارد
                update.reply("در حال ساخت ویس...")
                trans =GoogleTranslator('auto','fa').translate(voice_text)

                # پردازش ویس با محتوای دریافت شده
                rs = processing_voice(voice_text, 'voice.mp3')

                # ارسال فایل صوتی
                with open("voice.mp3", 'rb') as voice_file:
                    update.reply_voice('voice.mp3', caption=f"ویس شما آماده شد ومعنی ویس شما :\n{trans}")
                    
       
        except Exception as e:
            update.reply(f"خطایی رخ داد: {str(e)}")   
        finally:
            if os.path.exists("voice.mp3"):
                os.remove("voice.mp3")


                
@bot.on_message_updates(filters.is_group , filters.text)  # دریافت پیام‌های متنی در گروه‌ها
async def get_weather_info(update: Updates):
    user_input = update.text.strip()
    if not check_status():
        return

    # اگر پیام با کلمه "هوا" شروع می‌شود
    if user_input.startswith("هوا"):
        user_input = user_input.replace("هوا", "").strip()

        # اگر ورودی خالی است، پیام ارسال کنیم که نام شهر را وارد کند
        if not user_input:
            await update.reply("لطفاً نام شهری که می‌خواهید وضعیت آب و هوا را برای آن بررسی کنید، وارد کنید.")
            return

        # ارسال پیام "در حال پردازش..."
        processing_message = await update.reply("در حال پردازش... لطفاً صبر کنید.")

        # دریافت وضعیت آب و هوا
        weather_info = get_weather(user_input)

        # اگر پاسخ وضعیت آب و هوا خطا نباشد، ادامه می‌دهیم
        if "یافت نشد" not in weather_info:
            # ترجمه وضعیت آب و هوا به زبان انگلیسی
            translated_info = translate_text(weather_info, target_language='en')

            # ارسال وضعیت آب و هوا به زبان فارسی
            await update.reply(f"\nوضعیت آب و هوا به فارسی:\n{weather_info}")

            # ارسال وضعیت به زبان انگلیسی
            
        else:
            # در صورت بروز خطا، پیامی ارسال می‌شود
            await update.reply(weather_info)

 
 
@bot.on_message_updates(filters.is_group, filters.Commands(["تاریخ", "زمان"], prefixes=''))
def send_data(update: Updates):
    if not check_status():
        return
    # زمان فعلی به شمسی
    current_time_jalali = JalaliDatetime.today().strftime("%A %d %B %Y")
    
    # زمان فعلی به میلادی
    current_time_gregorian = datetime.now()
    gregorian_date = current_time_gregorian.strftime("%A %d %B %Y - %H:%M:%S")

    if current_time_gregorian.hour < 12:
        day_night = "روز بخیر"
    else:
        day_night = "شب بخیر"
    # ساخت متن خروجی به صورت یک رشته
    result = (
        f"{day_night}!\n\n"
        f"تاریخ به شمسی:\n{current_time_jalali}\n"
        f"تاریخ به میلادی:\n{gregorian_date}"
    )
    # ارسال پیام به گروه
    update.reply(result)

    
@bot.on_message_updates(filters.is_group)
def font(update: Updates):
    if not check_status():
        return
    # بررسی اینکه آیا پیام با "font" یا "فونت" شروع می‌شود
    if update.text.startswith("font") or update.text.startswith("فونت"):
        lang = "en" if update.text.startswith("font") else "fa"
        user_input = update.text.replace("font", "").replace("فونت", "").strip()
        
        # پیام انتظار
        update.reply("لطفاً صبر کنید تا فونت ساخته شود...")

        try:
            # دریافت فونت‌ها از API
            fonts = get_fonts(user_input, lang)

            if fonts:
                formatted_fonts = format_fonts(fonts)
                update.reply(f"فونت‌های شما:\n{formatted_fonts}")
                
            else:
                update.reply("فونتی یافت نشد!")
        
        except Exception as e:
            update.reply(f"خطا:\n{str(e)}")  

 


    
    

                

@bot.on_message_updates(filters.is_group)
def ancientline(update: Updates):
    if not check_status():
        return
    input_text = update.text.strip()
    
    if input_text.startswith("باستانی"):
        # حذف "باستانی" از ابتدای متن
        input_text = input_text.replace("باستانی", "", 1).strip()
        
        # تبدیل متن به خطوط مختلف
        cuneiform_output = convert_to_cuneiform(input_text)
        pahlavi_output = convert_to_pahlavi(input_text)
        manavi_output = convert_to_manichaean(input_text)
        hieroglyph = convert_to_hieroglyph(input_text)
        hw = GoogleTranslator(source='auto', target='iw').translate(input_text)
        linear_b_optimized = text_to_linear_b_optimized(input_text)
        update.reply('**در حال تبدیل متن شما به خطوط باستانی..**')
        # ارسال پیام تبدیل خطوط باستانی
        response = (
            f"**زبا های باستانی تبدیل شده :**\n\n"
            f"متن به خط میخی:\n{cuneiform_output}\n\n"
            f"متن به خط پهلوی:\n{pahlavi_output}\n\n"
            f"متن به خط مانوی:\n{manavi_output}\n\n"
            f"متن به خط هیروگلیف مصری:\n{hieroglyph}\n\n"
            f"متن به خط عبری باستانی:\n{hw}\n\n"
            f"متن به خط میکنی:\n{linear_b_optimized}\n\n"
        )
        
        # ارسال پاسخ نهایی
        update.reply(response)
        




@bot.on_message_updates(filters.is_group)
def send_logo(update: Updates):
    if not check_status():
        return
    input_text = update.text.strip()
    
  
    if input_text.startswith("lego"):
        
        logo_text = input_text.replace("lego", "").strip()
        
        # پیام موقت به کاربر
        update.reply("در حال ساخت لگو...")
        
        # تولید لوگو با متن ورودی
        logo_file = create_random_logo(logo_text)
        
        # ارسال عکس لوگو به کاربر
        update.reply_photo(logo_file, caption="لگوی شما آماده شد!")
        
        # حذف فایل لوگو بعد از ارسال برای جلوگیری از پر شدن حافظه
        os.remove(logo_file)

@bot.on_message_updates(filters.is_group,filters.Commands(["ارز"],prefixes=''))
async def coin_prices(update: Updates):
    
    if not check_status():
        return
    await update.reply("در حال به‌دست آوردن قیمت ارز...")
    try:
        # درخواست به وب‌سرویس برای دریافت قیمت ارزها
        response = requests.get('https://api.fast-creat.ir/nobitex?apikey=5151884791:6WORUy4LAz3J5KM@Api_ManagerRoBot')
        if response.status_code == 200:
            nobitex_data = response.json().get('result', {})

            # لیست قیمت‌ها به تومان
            arz_aig = [
                f"💰 بیتکوین (BTC): {nobitex_data.get('btc', 0) / 10:,.0f} تومان",
                f"💰 اتریوم (ETH): {nobitex_data.get('eth', 0) / 10:,.0f} تومان",
                f"💰 لایت کوین (LTC): {nobitex_data.get('ltc', 0) / 10:,.0f} تومان",
                f"💰 ترون (TRX): {nobitex_data.get('trx', 0) / 10:,.0f} تومان",
                f"💰 تون کوین (TON): {nobitex_data.get('ton', 0) / 10:,.0f} تومان",
                f"💰 دوجکوین (DOGE): {nobitex_data.get('doge', 0) / 10:,.0f} تومان"
            ]
            
            # ارسال لیست قیمت‌ها به عنوان پاسخ
            await update.reply("💲 قیمت ارزهای دیجیتال:\n" + '\n'.join(arz_aig))
        
        else:
            await update.reply("خطا در دسترسی به وب‌سرویس قیمت.")

    except Exception as e:
        await update.reply(f'مشکلی به وجود آمد. خطا: {e}')


            
            

@bot.on_message_updates(filters.is_group, filters.Commands(['لینک', 'link'], ''))
def send_group_link(update: Updates): 
    if not check_status():
        return
    group = update.object_guid
    if group:
        link = bot.get_group_link(update.object_guid)
        return  update.reply(f' بفرماید لینک گروه\n{link.join_link}')
    


    
    
@bot.on_message_updates(filters.is_group)
def game(update: Updates):
    global game_active
    if not check_status():
        return

    user_message = update.text.strip()

    # بررسی پیام‌ها و پاسخ‌دهی
    if user_message == "شروع":
        game_active = True
        update.reply("بازی شروع شد! لطفاً یکی از گزینه‌های زیر را وارد کنید:\n- سنگ\n- کاغذ\n- قیچی\n(برای پایان بازی، 'پایان' را وارد کنید.)")
    elif user_message == "پایان":
        game_active = False
        update.reply("بازی به پایان رسید! متشکرم که بازی کردید.")
    elif game_active:
        if user_message in choices:  # فقط اگر پیام یکی از گزینه‌ها باشد
            computer_choice = random.choice(choices)  # انتخاب تصادفی ربات

            # اعلام انتخاب ربات
            update.reply(f"ربات انتخاب کرد: {computer_choice}")

            # بررسی نتیجه
            if user_message == computer_choice:
                update.reply("تساوی!")
            elif (user_message == "سنگ" and computer_choice == "قیچی") or \
                 (user_message == "کاغذ" and computer_choice == "سنگ") or \
                 (user_message == "قیچی" and computer_choice == "کاغذ"):
                update.reply("شما برنده شدید!")
            else:
                update.reply("شما باختید!")
        else:
            return  # اگر پیام غیر مرتبط بود، هیچ پاسخی ندهید
    else:
        return  # هیچ پاسخی ندهید اگر بازی غیرفعال است



@bot.on_message_updates(filters.is_private)
def handle_message_add(update: Updates):
    
    global waiting_for_command, waiting_for_response, new_command
    if not check_status():
        return
    user_id = update.object_guid
    user_input = update.text.strip()
    if user_input.startswith('/command'):
        if user_id == ALLOWED_USER_ID:
            update.reply('لطفاً دستوری که می‌خواهید اضافه کنید را ارسال کنید.')
            waiting_for_command = True
        else:
            update.reply('شما مجاز به اضافه کردن دستورات نیستید.')
            
    elif waiting_for_command:
        
        new_command = user_input
        if new_command:
            try:
                update.reply(f'دستور {new_command} دریافت شد. حالا پاسخ را ارسال کنید.')
                waiting_for_command = False
                waiting_for_response = True
            except Exception as e:
                print(f"Error while sending message: {e}")
                update.reply('خطا در ارسال پیام. لطفاً دوباره تلاش کنید.')
        else:
            update.reply('دستور وارد شده خالی است. لطفاً یک دستور معتبر وارد کنید.')
    elif waiting_for_response:
        new_response = user_input  # ذخیره پاسخ
        add_command(new_command, new_response)  # ذخیره دستور و پاسخ در دیتابیس
        update.reply(f'دستور {new_command} با پاسخ `{new_response} ذخیره شد.')
        waiting_for_response = False  # غیرفعال کردن وضعیت دریافت پاسخ
    elif user_input == '/delete':
            if user_id == ALLOWED_USER_ID:
                
                delete_commands()
                
                update.reply('تمامی دستورات حذف شدند.')
                
            else:
                
                update.reply('شما مجاز به حذف دستورات نیستید.')
@bot.on_message_updates(filters.is_group)
def handle_message_group(update: Updates):
    if not check_status():
        return
    user_input = update.text.strip()
    response = get_response(user_input)
    if response:
        update.reply(response)


@bot.on_message_updates(filters.is_group,filters.Commands(['fal','فال'],prefixes=''))
def get_fal_and_send(update: Updates):
    update.reply("**منتظربمانید تابرایتان فال را اماد کنم**")
    if not check_status():
        return
    url = "https://api.api-code.ir/fallhafez2/index.php"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data['status'] == 200:
            result = data['result']
            number = result['number']
            ghazal = result['ghazal']
            voice = result['voice']
            tabir = result['tabir']
            message = f"📜 شماره غزل: {number}\n\n📝 متن غزل:\n{ghazal}\n\n🔮 تعبیر:\n{tabir}"
            update.reply(message)
            audio_response = requests.get(voice)
            audio_file = "voice_fal.mp3"
            with open(audio_file, 'wb') as f:
                f.write(audio_response.content)
                update.reply('به زودی ویس فال شما اماده میشه')
                update.reply_voice(audio_file,caption='بفرماید ویس فال شما')
        else:
            update.reply("مشکلی در دریافت فال وجود دارد.")
    else:
        update.reply(f"خطا در ارتباط با وب‌سرویس: {response.status_code}")


 



    






@bot.on_message_updates(filters.is_group)
async def start_report(message: Updates):
    if not check_status():
        return
    info = """
# توضیحات ربات

این ربات به کاربران اجازه می‌دهد تا گزارشی از یک کاربر دیگر یا محتوای خاصی را ارسال کنند. فرآیند ارسال گزارش به صورت مرحله به مرحله انجام می‌شود. کاربر باید ابتدا یک شناسه ارسال کند و سپس نوع تخلف را مشخص کند. در نهایت ربات گزارشات را ارسال می‌کند.

## مراحل عملکرد ربات

1. **شروع مکالمه با ربات**:
   - هنگامی که کاربر دستور /start را ارسال می‌کند، ربات شروع به کار می‌کند.
   - ربات از کاربر می‌خواهد که شناسه (object_guid) مربوط به فرد یا محتوایی که قصد گزارش آن را دارد، وارد کند.

2. **دریافت شناسه و انتخاب نوع تخلف**:
   - پس از دریافت شناسه، ربات از کاربر می‌خواهد که نوع تخلف را انتخاب کند. کاربر می‌تواند یکی از 7 گزینه زیر را انتخاب کند:
     1. محتوای مستهجن
     2. خشونت
     3. اسپم
     4. کودک‌آزاری
     5. نقض حق‌نشر
     6. فیشینگ
     7. سایر
     8. انتخاب تصادفی (راندم)

3. **توضیح تخلف "سایر"**:
   - اگر کاربر گزینه "سایر" یا "تصادفی" را انتخاب کند، ربات از او می‌خواهد توضیح مختصری در مورد نوع تخلف وارد کند.

4. **دریافت تعداد گزارش‌ها**:
   - بعد از انتخاب نوع تخلف، ربات از کاربر درخواست می‌کند که تعداد گزارش‌هایی که می‌خواهد ارسال شود را وارد کند.

5. **ارسال گزارش‌ها**:
   - پس از دریافت تعداد گزارش‌ها، ربات به تعداد درخواست‌شده گزارش‌ها را ارسال می‌کند.
   - پس از موفقیت در ارسال، به کاربر اطلاع داده می‌شود.

6. **حذف اطلاعات کاربر**:
   - پس از ارسال گزارش، تمامی داده‌های مربوط به کاربر از حافظه ربات پاک می‌شود تا اطلاعات کاربر ذخیره نشود.

7. **حذف دستی اطلاعات با دستور /delete**:
   - کاربر می‌تواند در هر مرحله با ارسال دستور /delete تمامی اطلاعات خود را از حافظه ربات پاک کرده و فرآیند را از ابتدا شروع کند.

## توضیحات درباره فیلترینگ

این ربات به شما کمک می‌کند تا گزارشاتی را ارسال کنید. لازم به ذکر است که ما موتور فیلترینگ نیستیم. در صورتی که گزارشی ارسال کنید و تعداد گزارش‌های شما بالا برود، ربات رسمی روبیکا به این گزارشات رسیدگی خواهد کرد و در صورت وجود تخلف واقعی، ممکن است اقدام به فیلتر کردن حساب کاربر نماید. 

به یاد داشته باشید که این ربات یک ربات گزارش‌دهی غیررسمی است و مدیران روبیکا از آن اطلاع ندارند. در آینده، اگر قابلیت فیلتر کردن به ربات اضافه شود، باید با رعایت قوانین و دقت لازم با این ربات کار کنید، زیرا اشتباه در گزارش‌ها ممکن است منجر به آسیب به حساب شما شود. 

از همکاری شما سپاسگزاریم. ربات گزارش‌دهی غیررسمی!
"""
    user_id = message.author_guid
    group =message.object_guid
    if group and await message.is_admin(user_guid=message.author_guid):
        
        if message.text == "/help":
            await message.reply(info)
            return

        # حذف داده‌ها در صورت دستور /delete
        if message.text == "/delete":
            if user_id in user_data:
                user_data.pop(user_id)
            await message.reply("داده‌های شما حذف شد. لطفاً دوباره دستور /start را وارد کنید.")
            return

        # مرحله اول: شروع گفتگو و درخواست شناسه
        if message.text == "/start":
            await message.reply(
        "✨ سلام و درود! به ربات گزارش‌دهی خوش آمدید. ✨\n\n"
        "لطفاً شناسه (object_guid) مربوط به کاربری که می‌خواهید گزارش کنید را ارسال نمایید.\n"
        "📚 اگر با نحوه کارکرد ربات آشنا نیستید، می‌توانید با ارسال دستور `/help` اطلاعات بیشتری دریافت کنید.\n\n"
        "🔧 **برای پشتیبانی، لطفاً با من تماس بگیرید:** (@Sepah_cyber84)\n"
    )

        

            user_data[user_id] = {"step": "waiting_for_guid"}  # ذخیره مرحله

        # مرحله دوم: دریافت شناسه و درخواست نوع تخلف
        elif user_data.get(user_id, {}).get("step") == "waiting_for_guid":
            object_guid = message.text
            user_data[user_id]["object_guid"] = object_guid  # ذخیره شناسه
            await message.reply("نوع تخلف را انتخاب کنید:\n1. محتوای مستهجن\n2. خشونت\n3. اسپم\n4. کودک‌آزاری\n5. نقض حق‌نشر\n6. فیشینگ\n7. سایر\n8. تصادفی")
            user_data[user_id]["step"] = "waiting_for_report_type"  # تغییر مرحله

        # مرحله سوم: دریافت نوع تخلف و درخواست توضیحات برای تخلف "سایر" (در صورت انتخاب)
        elif user_data.get(user_id, {}).get("step") == "waiting_for_report_type":
            report_type = message.text
            report_type_enum = None
            
            if report_type == '1':
                report_type_enum = ReportType.PORNOGRAPHY
                report_name = "محتوای مستهجن"
            elif report_type == '2':
                report_type_enum = ReportType.VIOLENCE
                report_name = "خشونت"
            elif report_type == '3':
                report_type_enum = ReportType.SPAM
                report_name = "اسپم"
            elif report_type == '4':
                report_type_enum = ReportType.CHILD_ABUSE
                report_name = "کودک‌آزاری"
            elif report_type == '5':
                report_type_enum = ReportType.COPYRIGHT
                report_name = "نقض حق‌نشر"
            elif report_type == '6':
                report_type_enum = ReportType.FISHING
                report_name = "فیشینگ"
            elif report_type == '7':
                report_type_enum = ReportType.OTHER
                report_name = "سایر"
                await message.reply("لطفاً توضیح مربوط به تخلف 'سایر' را وارد کنید:")
                user_data[user_id]["step"] = "waiting_for_other_description"  # تغییر مرحله به دریافت توضیح
                user_data[user_id]["report_type"] = report_type_enum  # ذخیره نوع تخلف
                return  # صبر تا دریافت توضیحات
            elif report_type == '8':  # انتخاب تصادفی
                random_types = [ReportType.PORNOGRAPHY, ReportType.VIOLENCE, ReportType.SPAM, ReportType.CHILD_ABUSE, ReportType.COPYRIGHT, ReportType.FISHING, ReportType.OTHER]
                report_type_enum = random.choice(random_types)  # انتخاب تصادفی
                report_name = "تصادفی"
            else:
                await message.reply("لطفاً یک عدد معتبر (1 تا 8) انتخاب کنید.")
                return
            
            user_data[user_id]["report_type"] = report_type_enum  # ذخیره نوع تخلف
            await message.reply(f"تخلف انتخاب‌شده: {report_name}. لطفاً تعداد گزارش‌هایی که می‌خواهید ارسال شود را وارد کنید:")
            user_data[user_id]["step"] = "waiting_for_report_count"  # تغییر مرحله

        # مرحله چهارم: دریافت توضیحات برای تخلف "سایر"
        elif user_data.get(user_id, {}).get("step") == "waiting_for_other_description":
            other_description = message.text
            user_data[user_id]["description"] = other_description  # ذخیره توضیح "سایر"
            await message.reply(f"توضیحات ثبت شد: {other_description}. حالا تعداد گزارش‌هایی که می‌خواهید ارسال شود را وارد کنید:")
            user_data[user_id]["step"] = "waiting_for_report_count"  # تغییر مرحله

        # مرحله پنجم: دریافت تعداد گزارش و ارسال نهایی
        elif user_data.get(user_id, {}).get("step") == "waiting_for_report_count":
            try:
                report_count = int(message.text)
                if report_count <= 0:
                    raise ValueError("عدد معتبر وارد کنید.")
            except ValueError:
                await message.reply("لطفاً یک عدد معتبر برای تعداد گزارش‌ها وارد کنید.")
                return
            
            # ارسال گزارشات به تعداد درخواست‌شده با فاصله زمانی 2 ثانیه
            object_guid = user_data[user_id]["object_guid"]
            report_type_enum = user_data[user_id]["report_type"]
            description = user_data[user_id].get("description", None)  # بررسی توضیحات "سایر"
            
            try:
                for _ in range(report_count):
                
                    await bot.report_object(object_guid, report_type_enum, description)
                    rep = random.uniform(1, 8.5)
                    
                    await asyncio.sleep(rep)  # فاصله زمانی 2 ثانیه‌ای بین هر گزارش
                

                await message.reply(f"گزارش با موفقیت ارسال شد. تعداد گزارش‌ها: {report_count}")
            except Exception as e:
                await message.reply(f"خطا در ارسال گزارش: {str(e)}")
            
            # پاک کردن اطلاعات کاربر پس از اتمام
            user_data.pop(user_id)

@bot.on_message_updates(filters.is_group)
def get_info_and_download_profile_picture(message: Updates):
    if not check_status():
        
        return
    
    if message.text.startswith("info:"):
        message.reply('منتظربمانید')
        
        # استخراج نام کاربری از پیام
        u = message.text.replace("info:", "").strip()
        
        try:
            # گرفتن اطلاعات کاربر بر اساس نام کاربری
            user = bot.get_object_by_username(u)
            
            
            if user:
                # دریافت اطلاعات کاربر با استفاده از متد `get`
                user_guid = user['user'].get('user_guid', None)
                username = user['user'].get('username', None)
                first_name = user['user'].get('first_name', None)
                bio = user['user'].get('bio', None)

                # چک کردن وجود اطلاعات قبل از دانلود
                if user_guid and username and first_name:
                    # دانلود عکس پروفایل
                    profile_picture_data = bot.download_profile_picture(user_guid)

                    # ذخیره کردن عکس در فایل
                    profile_picture_path = f"{username}_profile_picture.jpg"
                    with open(profile_picture_path, "wb") as f:
                        f.write(profile_picture_data)

                    # ساخت پیام برای ارسال اطلاعات کاربر و عکس پروفایل
                    result = f"""
🌟 **اطلاعات کاربر:**

👤 **نام کاربری:** @{username}  
📝 **نام:** {first_name}  
🆔 **گوید کاربر:** {user_guid if user_guid else 'ندارد'}  
📄 **بیوگرافی:** {bio if bio else 'ندارد'}  
📞 **شماره:** وضعیت بسته
                    """
                    
                    # ارسال عکس پروفایل همراه با اطلاعات
                    message.reply_photo(photo=profile_picture_path, caption=result)
                else:
                    # در صورت عدم وجود اطلاعات، پیام مناسب ارسال می‌شود
                    message.reply("❗️ کاربر دارای اطلاعات کافی نیست یا یافت نشد.")
            else:
                message.reply("❗️ کاربر یافت نشد.")
                
        except Exception as e:
            message.reply("⚠️ مشکلی در دسترسی به اطلاعات کاربر یا دانلود عکس پروفایل رخ داده است.")
            print(f"خطا: {e}")


@bot.on_message_updates(filters.is_group,filters.Commands(['بیو','بیوگرافی'],prefixes=''))
def send_bio(message: Updates):
    if not check_status():
        return
    bio =bio_fackt_faz.get_bio()
    
    
    
    res =random.choice(bio)
    message.reply(res)
@bot.on_message_updates(filters.is_group,filters.Commands(['عجایب','فکت'],prefixes=''))
def send_fackts(message: Updates):
    if not check_status():
        return
    fackt =bio_fackt_faz.get_facts()
    res =random.choice(fackt)
    message.reply(res)

@bot.on_message_updates(filters.is_group,filters.Commands(['طنز','جوک'],prefixes=''))
def send_jock(message: Updates) :
    if not check_status():
        return
    jock=bio_fackt_faz.get_jock()
    res=random.choice(jock)
    message.reply(res)
    
    


    
@bot.on_message_updates(filters.is_group,filters.Commands(['انگیزه','انگیزشی','امید'],prefixes=''))
def getpoem(message: Updates) :
    if not check_status():
        return
    m =bio_fackt_faz.get_motivation()
    
    res=random.choice(m)
    
    message.reply(res)
    
@bot.on_message_updates(filters.is_group)
def tranlate(message: Updates) :
    text = message.text.strip()
    if not check_status():
        return
    if text.startswith("ترجمه "):  # مطمئن شویم متن به‌درستی با "ترجمه" شروع می‌شود
        message.reply("در حال پردازش... لطفاً صبر کنید 🕒")
        
        text_to_translate = text.replace("ترجمه ", "").strip()  # حذف "ترجمه" و فضای اضافی
        if not text_to_translate:
            message.reply("متنی برای ترجمه وارد نشده است. لطفاً متن خود را پس از 'ترجمه' وارد کنید.")
            return
        
        try:
            # ترجمه متن به فارسی
            translated_text = GoogleTranslator(source='auto', target='fa').translate(text_to_translate)
            message.reply(f"🔄 ترجمه شما: \n\n{translated_text}")
        except Exception as e:
            message.reply("⚠️ مشکلی در ترجمه متن رخ داده است. لطفاً دوباره امتحان کنید.")
            print(f"Error during translation: {e}")

@bot.on_message_updates(filters.is_group)
def prayer_timess(message: Updates):
    if not check_status():
        return
    text = message.text.replace('شرعی', "").strip()  
    if message.text.startswith("شرعی"):
        message.reply("در حال پردازش... لطفاً صبر کنید 🕒")
        timings =prayer_times.get_prayer_times(text)
        
        if timings:
            result = (
                f"اوقات شرعی برای {text}:\n"
                f"صبح: {timings['Fajr']}\n"
                f"ظهر و عصر: {timings['Dhuhr']}\n"
                f"مغرب و عشا: {timings['Maghrib']}"
            )
            message.reply(result)  
        else:
            message.reply('شهر نامعتبر است یا اطلاعاتی در دسترس نیست.')
  

        
@bot.on_message_updates(filters.is_group,filters.Commands(['ترسناک','اجنه','ارواح'],prefixes=''))
def get_fery(message: Updates)  :
    if not check_status():
        return
    tarsnak =bio_fackt_faz.get_fear()
    
    res=random.choice(tarsnak)
    message.reply(res)

@bot.on_message_updates(filters.is_group,filters.Commands(['حدیث'],prefixes=''))
def send_hadic(message: Updates):
    if not check_status():
        return
    h=bio_fackt_faz.get_hadis()
    res=random.choice(h)
    message.reply(res)
    
  


    
@bot.on_message_updates(filters.is_group,filters.Commands(['دیالوگ','صدا'],prefixes='')) 
def send_love(message: Updates):
    if not check_status():
        return
    d=bio_fackt_faz.get_dialog()
    res=random.choice(d)  
    message.reply(res)
    
@bot.on_message_updates(filters.is_group,filters.Commands(['دانستنی'],prefixes='')) 
def send_love(message: Updates):
    if not check_status():
        return
    d=bio_fackt_faz.get_danestani()
    res=random.choice(d)  
    message.reply(res)
    


@bot.on_message_updates(filters.is_group,filters.Commands(['شماره'],prefixes=''))
def send_number(message: Updates):
    if not check_status():
        return
    phone_number, operator = generate_phone_number()
    message.reply(f"شماره تصادفی شما: {phone_number}\nاپراتور: {operator}")

    
    
@bot.on_message_updates(filters.Commands(['موزیک'],prefixes=''), filters.is_group)
async def music(update: Updates):
    if not check_status():
        return
    user_id = update.object_guid

    # اگر کاربری در حال استفاده از ربات است، به کاربر جدید پاسخ داده نشود
    if any('style' in user for user in user_data.values()):
        await update.reply("لطفاً صبر کنید، یک کاربر دیگر در حال استفاده از ربات است.")
        return

    # ایجاد دیکشنری جدید برای ذخیره اطلاعات کاربر
    user_data[user_id] = {}

    welcome_message = (
        "سلام! 🎶\n"
        "من یک ربات برای ساخت آهنگ هستم. با استفاده از لیست زیر می‌توانید یک سبک موسیقی انتخاب کنید.\n\n"
        "لطفاً عدد مرتبط با سبک مورد نظر را وارد کنید:\n\n"
    )
    styles = "\n".join(music_styles)
    await update.reply(welcome_message + styles)

# هندلر برای نمایش راهنما
@bot.on_message_updates(filters.Commands(['کمک'],prefixes=''), filters.is_group)
async def help_command(update: Updates):
    if not check_status():
        return
    help_message = (
        "/موزیک - شروع و انتخاب سبک موسیقی\n"
        "/کمک - دریافت راهنما\n"
        "پس از انتخاب سبک، از شما خواسته می‌شود متن آهنگ خود را وارد کنید."
    )
    await update.reply(help_message)

# هندلر برای دریافت سبک و متن آهنگ
@bot.on_message_updates(filters.is_group)
async def choose_style(update: Updates):
    user_id = update.object_guid
    if not check_status():
        return

    # فقط به کاربرانی که دستور "/موزیک" را فرستاده‌اند پاسخ بدهد
    if user_id not in user_data:
        return

    # اگر کاربر هنوز سبکی انتخاب نکرده
    if 'style' not in user_data[user_id]:
        try:
            # دریافت شماره انتخابی کاربر
            style_index = int(update.message.text.strip()) - 1
            if 0 <= style_index < len(music_styles):
                style_name = music_styles[style_index].split("- ")[1]
                user_data[user_id]['style'] = style_name
                await update.reply(f"سبک {style_name} انتخاب شد. 🎶\nحالا متن آهنگ رو ارسال کن:")
            else:
                await update.reply("لطفاً یک عدد معتبر انتخاب کنید.")
        except ValueError:
            await update.reply("لطفاً یک عدد معتبر انتخاب کنید.")

    # دریافت متن آهنگ
    elif 'text' not in user_data[user_id]:
        user_data[user_id]['text'] = update.message.text.strip()
        await update.reply("منتظر باش تا آهنگت ساخته بشه 🎵...")

        # ساخت موسیقی با API
        style = user_data[user_id]['style']
        text = user_data[user_id]['text']
        music_url = await create_music(style, text)

        if music_url:
            # دانلود و ارسال آهنگ به کاربر
            await send_music(update, music_url)
        else:
            await update.reply("مشکلی در ساخت موسیقی پیش آمد. لطفاً دوباره امتحان کنید.")

        # پاک کردن دیتا بعد از ارسال آهنگ
        del user_data[user_id]

# تابع برای ساخت موسیقی با API
async def create_music(style, text):
    api_url = "https://api.api-code.ir/c-music/"
    params = {
        "style": style.replace(' ', '').lower(),  # تغییر سبک به فرمت مناسب برای API
        "text": text.replace(' ', '+')  # جایگزینی فاصله‌ها با + برای API
    }
    
    try:
        response = requests.get(api_url, params=params)
        if response.status_code == 200:
            data = response.json()
            if data["status"] == "success":
                return data["music_url"]
        return None
    except Exception as e:
        print(f"Error in API request: {e}")
        return None

# تابع برای دانلود و ارسال موسیقی
async def send_music(update: Updates, music_url):
    try:
        music_response = requests.get(music_url)
        if music_response.status_code == 200:
            file_name = "music.mp3"
            with open(file_name, "wb") as f:
                f.write(music_response.content)
            await update.reply('منتظربمانید تا پردازش کنیم')
            # ارسال فایل موسیقی به کاربر
            await update.reply_document(file_name, caption="این هم آهنگت 🎵")
        else:
            await update.reply("مشکلی در دانلود موسیقی پیش آمد.")
    except Exception as e:
        print(f"Error in downloading music: {e}")
        await update.reply("مشکلی در دانلود موسیقی پیش آمد.")
    


        
    
@bot.on_message_updates(filters.is_group)
async def riazi(update: Updates):
    expression = update.text.replace("ریاضی", "").strip()
    if not check_status():
        return
    if update.text.startswith("ریاضی"):
        await update.reply("درحال محاسبه")
        # بررسی وجود علامت سؤال
        if '?' in expression:
            await update.reply('لطفاً فرمت دستور را به درستی وارد کنید. مانند: `2 + 22` (بدون علامت سؤال)')
            return
        
        # بررسی فرمت ورودی
        if re.match(valid_expression_pattern, expression):
            try:
                # محاسبه نتیجه
                result = eval(expression)  # محاسبه نتیجه
                response = f'نتیجه {expression} برابر است با: {result}'
            except Exception as e:
                response = 'خطا در محاسبه: لطفاً عبارت ریاضی معتبری وارد کنید.'
        else:
            response = 'لطفاً فرمت دستور را به درستی وارد کنید. مانند: `2 + 22`'
        
        await update.reply(response)


    
    
    

 
@bot.on_message_updates(filters.is_group)
async def save_user_bot(update: Updates):
    text = update.text.strip()
    user_id = str(update.author_guid)  # استفاده از user_id منحصربه‌فرد برای هر کاربر
    if not check_status():
        return
    # بررسی فرمت پیام کاربر
    if text.startswith("بات:"):
        name = text.split("بات:")[1].strip()  # دریافت نام از پیام کاربر
        if name:
            save_user_name(user_id, name)  # ذخیره نام کاربر همراه با user_id
            await update.reply("نام شما با موفقیت ذخیره شد.")
        else:
            await update.reply("لطفاً نام خود را با فرمت صحیح وارد کنید: بات : [نام شما]")
    elif text == "بات":
        name = get_user_name(user_id)  # بازیابی نام کاربر بر اساس user_id
        if name:
            
            descriptions = [
    f"{name} عزیز، خوش‌آمدید!",
    f"{name} جان، از دیدنت خوشحالم!",
    f"{name} گرامی، در خدمت شما هستم!",
    f"به جمع ما خوش‌آمدید، {name} دوست عزیز!",
    f"{name} نازنین، قدومتان سرشار از لطف است!",
    f"{name} گرامی، حضورتان موجب افتخار است!",
    f"باعث خوشحالی است که شما را اینجا داریم، {name} عزیز!",
    f"{name} جان، حضور شما مایه دلگرمی است!",
    f"خوشحالم که همراه شما هستیم، {name} عزیز!",
    f"{name} دوست محترم، خوش آمدید و روز خوش!",
    f"چه سعادتی که شما را می‌بینیم، {name} گرامی!",
    f"{name} بزرگوار، حضور شما را گرامی می‌داریم!",
    f"{name} جان، باعث افتخار است که شما را در کنار خود داریم!",
    f"از همراهی شما خرسندیم، {name} عزیز!",
    f"{name} نازنین، به ما بپیوندید و لذت ببرید!",
    f"{name} جان، باعث دلگرمی ما هستید!",
    f"{name} گرامی، قدومتان مبارک باشد!",
    f"{name} دوست دوست‌داشتنی، به این جمع صمیمی خوش آمدید!",
    f"{name} عزیز، حضورتان سرشار از انرژی مثبت است!",
    f"{name} جان، از دیدار شما لذت می‌بریم!",
    f"{name} گرامی، همیشه در خدمت شما هستیم!",
    f"{name} نازنین، به گرمی از شما استقبال می‌کنیم!",
    f"{name} جان، حضورتان اینجا را نورانی کرده است!",
    f"{name} گرامی، به ما بپیوندید و از همراهی‌تان بهره ببریم!",
    f"{name} دوست محترم، دیدارتان مایه خوشوقتی است!",
    f"خوشحالیم که شما را کنار خود داریم، {name} عزیز!",
    
    f"{name} عزیز، به محفل ما خوش آمدید. دعای ما برای شما همیشه برقرار است!",
    f"{name} گرامی، از آمدنتان در این مکان نورانی خرسندیم. ان‌شاءالله روزگار شما سرشار از برکت باشد!",
    f"{name} جان، وجود شما در اینجا مایه برکت و رحمت است. خداوند شما را حفظ کند!",
    f"خوش آمدید، {name} بزرگوار! امید است این جمع بتواند الهام‌بخش شما باشد.",
    f"{name} عزیز، حضور شما موجب افتخار ماست. دعاگوی شما هستیم!",
    f"{name} گرامی، امید داریم که در این جمع رحمت الهی شامل حال شما باشد!",
    f"{name} نازنین، خوشحالیم که در این فضای معنوی با شما هستیم. خداوند همراه شما باشد!",
    f"به جمع ما خوش آمدید، {name} عزیز! ان‌شاءالله زندگی‌تان پر از خیر و برکت باشد.",
    f"{name} جان، امید است این جمع به شما آرامش و دلگرمی ببخشد!",
    f"{name} بزرگوار، از وجود شما در اینجا بسیار خرسندیم. خداوند همیشه یار و یاورتان باشد!",
    f"{name} گرامی، شما را به جمعی صمیمی و با محبت دعوت می‌کنیم. دعای خیر ما با شماست!",
    f"{name} عزیز، خوشحالیم که در کنار شما هستیم. امیدواریم این جمع برای شما آرامش‌بخش باشد!",
    f"{name} جان، دعای ما همیشه در حق شما جاری است. امیدواریم روزهای خوشی در پیش داشته باشید!",
    f"{name} بزرگوار، به جمع ما خوش آمدید. در کنار هم دعاگوی یکدیگر خواهیم بود.",
    f"{name} عزیز، امیدواریم از محضر پر برکت این جمع بهره‌مند شوید.",
    f"{name} جان، از حضورتان در این جمع معنوی بسیار خرسندیم. دعای ما همیشه با شماست!",
    f"{name} گرامی، شما در اینجا مایه برکت هستید. دعاگوی شما خواهیم بود!",
    f"{name} عزیز، خوشحالیم که در این جمع معنوی با شما هستیم. دعای ما همیشه با شماست!",
    f"{name} جان، خوشحالیم که در کنار شما هستیم. ان‌شاءالله همواره در مسیر نور و هدایت باشید!",
    f"{name} نازنین، به جمع ما خوش آمدید. امیدواریم از محضر پر برکت این جمع بهره‌مند شوید!",
    f"{name} عزیز، دعای ما برای شما در این جمع جاری است. امیدواریم زندگی‌تان پربرکت باشد!",
    f"{name} جان، خوشحالیم که در کنار شما هستیم. ان‌شاءالله همواره در مسیر هدایت باشید!",
    f"{name} بزرگوار، از همراهی شما بسیار خوشحالیم. خداوند شما را همیشه در پناه خود نگه دارد!"
]

  

            await update.reply(random.choice(descriptions))
        else:
            await update.reply("لطفاً ابتدا نام خود را با فرمت `بات : [نام شما]` وارد کنید.")       
    elif text.startswith("user"):
        users = get_all_users()  # بازیابی لیست کاربران
        if users:
            user_list = "\n".join(users)
            await update.reply(f"کاربران ذخیره‌شده:\n{user_list}")
        else:
            await update.reply("هیچ کاربری ذخیره نشده است.")  
@bot.on_message_updates(filters.is_group)
async def code_run(update: Updates):
    if not check_status():
        return
    text = update.text.strip()  # دریافت متن پیام
    if text.startswith("run:"):
        code = text.replace("run:", "", 1).strip()  # حذف "run:" و فضاهای اضافی
        await update.reply("در حال خروجی گرفتن...")  # اطلاع به کاربر

        result = await execute_code(code)  # اجرای کد و دریافت نتیجه

        # بررسی طول نتیجه
        if len(result) > 4096:  # اگر نتیجه بیشتر از 4096 کاراکتر باشد
            await update.reply("خروجی بسیار طولانی است، لطفاً کد را کوتاه‌تر کنید.")
        else:
            # ارسال نتیجه به کاربر
            await update.reply(f"نتیجه:\n{result}\n")
@bot.on_message_updates(filters.is_group,filters.Commands(['قفل'], prefixes=''))
async def lock_group(update: Updates):
    group = update.object_guid
    if not check_status():
        return
    if group and await update.is_admin(user_guid=update.author_guid):
    
        await bot.set_group_default_access(
            group_guid=group,
            access_list=[]  # حذف دسترسی ارسال پیام
        )
        await update.reply("✅ گروه قفل شد. کاربران نمی‌توانند پیام ارسال کنند.")
    
@bot.on_message_updates(filters.is_group , filters.Commands(['باز'], prefixes=''))
async def unlock_group(update: Updates):
    group = update.object_guid
    if not check_status():
        return
    if group and await update.is_admin(user_guid=update.author_guid):
        
    
        print("Unlocking group with GUID:", group)  # دیباگ GUID
        try:
            await bot.set_group_default_access(
                group_guid=group,
                access_list=["SendMessages"]  # فعال کردن ارسال پیام
            )
            await update.reply("🔓 گروه باز شد. اکنون کاربران می‌توانند پیام ارسال کنند.")
        except Exception as e:
            print("Error while unlocking group:", e)
            await update.reply("خطا در باز کردن گروه. لطفاً دوباره امتحان کنید.")
            
            



@bot.on_message_updates(filters.is_group,filters.Commands(['مداحی'],prefixes='')) 
async def send_random_audio(update: Updates):
    
    if not check_status():
        return
    guid =update.object_guid
    url = 'https://kashoob.com/playlist/9GOj9/%D9%85%D8%AF%D8%A7%D8%AD%DB%8C-%D9%87%D8%A7%DB%8C-%D8%AD%D9%85%D8%A7%D8%B3%DB%8C-%D9%85%D8%A8%D8%A7%D8%B1%D8%B2%D9%87-%D8%A8%D8%A7-%D8%A7%D8%B3%D8%B1%D8%A7%D8%A6%DB%8C%D9%84'
    
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    # پیدا کردن تمامی تگ‌های <div> که ویژگی data-url دارند
    audio_links = [div['data-url'] for div in soup.find_all('div', {'data-url': True})]
    await update.reply("درحال پردازش هستم به زودی درویسکال اجرا میشه ..")
    # اگر لینک‌ها موجود باشند
    if audio_links:
        # انتخاب یک لینک رندم از لیست
        audio_url = random.choice(audio_links)

        # ارسال لینک صوتی به چت
        await bot.voice_chat_player(guid,audio_url)
    else:
        await update.reply('هیچ فایل صوتی پیدا نشد.')
 
    

@bot.on_chat_updates(filters.text, filters.is_group)
async def check_join_leave(update: Updates):
    if not check_status():
        return

    message_text = update.text.lower()
    user_name = update.author_guid or "کاربر"  # نام کاربر یا پیش‌فرض
    current_time = datetime.now().strftime("%H:%M")  # زمان فعلی به‌صورت ساعت و دقیقه

    # شناسایی ورود کاربر
    if match_patterns(message_text, welcome_patterns):
        welcome_message = random.choice(welcome_messages)
        await update.reply(welcome_message.format(name=user_name, time=current_time))

    # شناسایی خروج کاربر
    elif match_patterns(message_text, farewell_patterns):
        farewell_message = random.choice(farewell_messages)
        await update.reply(farewell_message.format(name=user_name, time=current_time))

@bot.on_message_updates(filters.text,filters.is_group) 
async def updates_questions(update: Updates):
    message_text = update.text
    questions_and_answers=bio_fackt_faz.get_question()
    global last_question, last_answer
    if not check_status():
        return
    
    message_text = update.text

    if message_text == 'جواب':
        if last_question and last_answer:
            await update.reply(f"سوال: {last_question}\nجواب: {last_answer}")
        else:
            random_qa = random.choice(questions_and_answers)
            last_question = random_qa["question"]
            last_answer = random_qa["answer"]
            await update.reply(last_question)
    elif message_text == 'نفهمیدم':
        if last_question and last_answer:
            await update.reply(f"سوال: {last_question}\nجواب: {last_answer}")
        else:
            await update.reply("هیچ سوالی برای پاسخ دادن وجود ندارد.")
    elif message_text == 'بپرس':
        random_qa = random.choice(questions_and_answers)
        last_question = random_qa["question"]
        last_answer = random_qa["answer"]
        await update.reply(last_question)
        
@bot.on_message_updates(filters.text,filters.is_group,filters.Commands(['ذکر'],prefixes='')) 
async def send_zeker(update: Updates):
    if not check_status():
        return
    zekr_message = bio_fackt_faz.get_zeker()  # فراخوانی تابع ذکر
    
    await update.reply(zekr_message)
    
           
           
@bot.on_message_updates(filters.text,filters.is_group)
async def send_music_gapp(update: Updates):
    user_message = update.text.strip()
    if not check_status():
        return
    # بررسی شروع پیام با "سرچ"
    if user_message.startswith("ارسال"):
        await update.reply("صبرکنید لطفا ...")
        search_text = user_message[len("ارسال"):].strip()
        song_info = get_song(search_text)
        
        if "error" in song_info:
            await update.reply(song_info["error"])
        else:
            song_title = song_info["title"]
            song_url = song_info["song"]
            
            # اطلاع‌رسانی و ارسال آهنگ با متد reply_music
            await update.reply(f"آهنگ یافت شد: {song_title}\nدر حال ارسال آهنگ...")
            await update.reply_music(song_url, caption=f"آهنگ مورد نظر شما یافت شد:\n{song_title}")


@bot.on_message_updates(filters.text,filters.is_group)
async def send_music_voice_call(update: Updates) :
    if not check_status():
        return
    user_message = update.text.strip()
    guid =update.object_guid
    # بررسی شروع پیام با "سرچ"
    bot.leave_group_voice_chat()
    if user_message.startswith("سرچ"):
        await update.reply("صبرکنید لطفا ...")
        
        search_text = user_message[len("سرچ"):].strip()
        song_info = get_song(search_text)
        
        if "error" in song_info:
            await update.reply(song_info["error"])
        else:
            song_title = song_info["title"]
            song_url = song_info["song"]
            
            # اطلاع‌رسانی و ارسال آهنگ با متد reply_music
            await update.reply(f"آهنگ یافت شد: {song_title}\nدر حال ارسال آهنگ...")
            await bot.voice_chat_player(guid,song_url)
            await update.reply(f"آهنگ مورد نظر شما یافت شد ودرویسکال میتونید گوش کنید: \n{song_title}" )
            
            

        
    

    
             
@bot.on_message_updates(filters.text,filters.is_group,filters.Commands(['تفییر_لینک','منقضی','لینک_منقضی'],prefixes=''))    
async def set_new_group_link(update: Updates):
    if not check_status():
        return
    group_guid=update.object_guid
    if group_guid and await update.is_admin(user_guid=update.author_guid):
        
        new_link =await bot.set_group_link(group_guid)
        await update.reply(f"لینک نغییریافت وقبلی منقضی شد!.")
        
    
            
@bot.on_message_updates(filters.text,filters.is_group,filters.Commands(['استخاره'],prefixes=''))  
async def estekhare(update: Updates) :
    if not check_status():
        return
    await update.reply("درحال به درست اوردن استخاره")
    estekhare_data=fetch_estekhare()
    if estekhare_data:
        result = (
            f"📜 **نتیجه استخاره:**\n\n"
            f"**سوره:** {estekhare_data['result']['soreh']}\n"
            f"**آیه:** {estekhare_data['result']['ayeh']}\n"
            f"**نتیجه:** {estekhare_data['result']['natijeh']}\n"
            f"**نتیجه کلی:** {estekhare_data['result']['natijeh_kolli']}\n"
            f"**نتیجه ازدواج:** {estekhare_data['result']['natijeh_ezdevaj']}\n"
            f"**نتیجه معامله:** {estekhare_data['result']['natijeh_moameleh']}\n"
        )
        await update.reply(result)  # ارسال نتیجه به کاربر
    else:
        await update.reply("⚠️ مشکلی در دریافت اطلاعات استخاره پیش آمد. لطفا مجددا تلاش کنید.")

@bot.on_message_updates(filters.text , filters.is_group)
async def phone_info(update: Updates):
    if not check_status():
        return
    text = update.text.strip()

    # بررسی اینکه آیا متن با "number" شروع می‌شود یا نه
    if text.startswith("number"):
        phone_number = text[len("number"):].strip()  # حذف "number" و فضای خالی
        if phone_number:  # بررسی اینکه آیا شماره‌ای وجود دارد
            await update.reply("در حال یافتن اطلاعات شماره...")
            res = get_phone_info(phone_number)  # دریافت اطلاعات شماره
            await update.reply(res)  # ارسال اطلاعات به کاربر
        else:
            await update.reply("لطفاً شماره تلفن را وارد کنید. مثال: `number: +989123456789`")


@bot.on_message_updates(filters.text , filters.is_group)
async def send_qr_code(update: Updates):
    user_input = update.text.strip()
    if not check_status():
        return
    if user_input.startswith("qr:"):
        user_input =user_input.replace("qr","")
        await update.reply("در حال ایجاد کد QR از داده شما...")

        # ایجاد کد QR و دریافت مسیر تصویر
        img_path = create_qr_code(user_input)
        
        # ارسال تصویر کد QR به کاربر
        await update.reply_photo(photo=img_path)

        # حذف تصویر بعد از ارسال
        if os.path.exists(img_path):
            os.remove(img_path)

@bot.on_message_updates(filters.text , filters.is_group)          
async def find_emoji(update: Updates):
    if not check_status():
        return
    text = update.text
    response = find_emoji_response(text)

    if response:
        await update.reply(response)          
          
       
@bot.on_message_updates(filters.text , filters.is_group)
async def ip_addr(update: Updates):
    if not check_status():
        return
    text =update.text.strip()
    
    if text.startswith("ip:"):
        await update.reply("درحال به دست اوردن  ایپی سایت")
        text =text.replace("ip:","")
        
        res=get_ip_address(text)
        await update.reply(f"بفرماید اینم از ایپی این سایت :\n{text}\n ip :{res}")
        
        
@bot.on_message_updates(filters.text , filters.is_group,filters.Commands(['اخبار'],prefixes=''))
async def send_news(update: Updates):
    if not check_status():
        return
    # اگر کاربر "اخبار" ارسال کند
    await update.reply("در حال بارگذاری اخبار...")

    # دریافت اخبار
    news = fetch_latest_news()

    # آماده کردن پیام برای ارسال
    if news:
        message = "📢 جدیدترین اخبار:\n\n"
        for idx, news_item in enumerate(news, 1):
            message += f"{idx}. {news_item['title']}\n🔗 {news_item['url']}\n\n"
        
        # تقسیم پیام به بخش‌های کوچکتر
        message_parts = split_message(message)

        # ارسال هر بخش جداگانه
        for part in message_parts:
            await update.reply(part)
    else:
        await update.reply("هیچ خبری برای نمایش وجود ندارد.")     
    
@bot.on_message_updates(filters.music,filters.is_group)
async def handle_music_(update: Updates):
    if not check_status():
        return
    await update.reply("دریافت شد")
    guid =update.object_guid
    # دانلود و ذخیره موزیک
    file_path = await update.download(save_as="downloaded_music.mp3")
    await update.reply("موزیک شما دانلود و به ویسکال ارسال شد")
    
    # ارسال موزیک به چت
    with open("downloaded_music.mp3","rb") as m :
        # await bot.send_music(guid,'downloaded_music.mp3')
        await bot.voice_chat_player(guid,'downloaded_music.mp3')
@bot.on_message_updates(filters.text , filters.is_group,filters.Commands(['گویدم','شناسه_خودم'],prefixes=''))
async def send_guid_man(update: Updates): 
    if not check_status():
        return
    user_id = update.author_guid  # شناسه کاربر فرستنده پیام
    message_text = update.text.strip()  # متن پیام
    
    await update.reply(f"بفرماید اینم شناسه شما :\n{user_id}")
    

@bot.on_message_updates(filters.text , filters.is_group)
async def to_world(update: Updates):
    num_text = update.text
    if not check_status():
        return
    # بررسی اینکه آیا پیام با "حروف" شروع می‌شود
    if num_text.startswith("حروف"):
        await update.reply("درحال تبدیل به حروف...")
        
        # حذف کلمه "حروف" از متن
        num_text = num_text.replace("حروف", "").strip()
        
        # بررسی اینکه آیا مقدار باقی‌مانده یک عدد است
        if num_text.isdigit():
            num = int(num_text)
            world = num2words(num, lang='fa')
            await update.reply(f"عدد شما به حروف:\n{world}")
        else:
            
            await update.reply("لطفاً یک عدد معتبر وارد کنید.")
    



async def manage_voice_chat(action: str, group_guid: str, user_guid: str, update: Updates):
    """
    مدیریت ویس چت (ایجاد یا خروج).
    
    Args:
        action (str): "start" برای ایجاد یا "leave" برای خروج.
        group_guid (str): آیدی گروه.
        user_guid (str): آیدی کاربر ارسال‌کننده دستور.
        update (Updates): آبجکت آپدیت برای ارسال پیام پاسخ.
    """
    try:
        # اطمینان از اینکه کاربر مدیر است
        if not await update.is_admin(user_guid=user_guid):
            await update.reply("❗ شما دسترسی لازم برای این عملیات را ندارید.")
            return
        
        if action == "start":
            # ایجاد ویس چت
            result = await bot.create_group_voice_chat(group_guid=group_guid)
            voice_chat_id = result["group_voice_chat_update"]["voice_chat_id"]
            
            # ذخیره آیدی ویس چت
            active_voice_chats[group_guid] = voice_chat_id
            await update.reply("🎙 ویس چت با موفقیت ایجاد شد.")
        
        elif action == "leave":
            # بررسی وجود ویس چت فعال
            voice_chat_id = active_voice_chats.get(group_guid)
            if not voice_chat_id:
                await update.reply("❗ ویس چت فعالی برای خروج یافت نشد.")
                return
            
            # خروج از ویس چت
            await bot.leave_group_voice_chat(group_guid=group_guid, voice_chat_id=voice_chat_id)
            await update.reply("🔇 ویس چت با موفقیت قطع شد.")
            
            # حذف آیدی ویس چت از دیکشنری
            del active_voice_chats[group_guid]
        
        else:
            await update.reply("❗ دستور نامعتبر. لطفاً از دستورات صحیح استفاده کنید.")
    
    except Exception as e:
        await update.reply(f"❗ خطایی رخ داده است: {e}")

# دستور برای ایجاد ویس چت
@bot.on_message_updates(filters.text , filters.Commands(['CALL', 'call', 'کال'], prefixes=''))
async def start_voice_chat(update: Updates):
    if not check_status():
        return
    group = update.object_guid
    if group:
        await manage_voice_chat(action="start", group_guid=group, user_guid=update.author_guid, update=update)

# دستور برای خروج از ویس چت
@bot.on_message_updates(filters.text , filters.Commands(['قطع'], prefixes=''))
async def leave_voice_chat(update: Updates):
    if not check_status():
        return
    group = update.object_guid
    if group:
        await manage_voice_chat(action="leave", group_guid=group, user_guid=update.author_guid, update=update)

    
    
    
    
  
       
@bot.on_message_updates(filters.text , filters.is_group,filters.Commands(['گوید_گپ','شناسه_گروه'],prefixes=''))
async def send_guid_gapp(update: Updates):
    guid =update.object_guid
    if not check_status():
        return
    await update.reply(f"شناسه گپ فعلی شما :\n{guid }")

@bot.on_message_updates(filters.text , filters.is_group , filters.Commands(['کلیپ','ویدیو'], prefixes=''))
async def send_clip(update: Updates):
    if not check_status():
        return
    await update.reply("درحال  ارسال ویدیو")
    video_url, caption = fetch_video()
    if video_url:
        await update.reply_video(video_url,caption=caption or "ویدیویی از API")
    else :
        await update.reply("❌ متأسفانه قادر به دریافت ویدیو نیستم. لطفاً مجدداً تلاش کنید.")


@bot.on_message_updates(filters.is_group , filters.Commands(['پروفایل'], prefixes=''))
async def send_profile(update: Updates):
    r_prof =fetch_prof()
    if not check_status():
        return
    if r_prof:
        await update.reply_photo(r_prof,caption="پروفایل شما ")
    
    
@bot.on_message_updates(filters.is_group, filters.Commands(['تاس'], prefixes=''))
async def send_dice(update: Updates):
    if not check_status():
        
        return
    # تولید یک عدد تصادفی بین 1 تا 6 به عنوان نتیجه تاس
    dice_result = random.randint(1, 6)
    
    # تعریف پیام‌های مختلف بر اساس نتیجه‌ی تاس
    dice_messages = {
        1: "🎲 تاس رو انداختی و عدد **1** اومد! به نظر میاد شانس امروز باهات همراه نیست! 😅",
        2: "🎲 تاس انداختی و عدد **2** شد! شاید دفعه‌ی بعد خوش‌شانس‌تر باشی! 🤞",
        3: "🎲 نتیجه تاس **3** شد! میانه‌رو هستی، شانس با تو نیمه همراهه! 😌",
        4: "🎲 این بار نتیجه تاس **4** شد! بد نیست، اما هنوز جا برای بهتر شدن هست! 👌",
        5: "🎲 خوش‌شانس بودی! نتیجه **5** شد! یه قدم مونده تا عالی! 🍀",
        6: "🎲 واااای! تاس عدد **6** اومد! شانس کامل با توست، عالی بود! 🎉🥳"
    }
    
    # گرفتن پیام متناسب با نتیجه تاس
    message = dice_messages[dice_result]
    
    # ارسال پیام نتیجه‌ی تاس به گروه
    await update.reply(message)
            
             
            
        
@bot.on_message_updates(filters.is_group, filters.Commands(['خاطره'], prefixes='')) 
async def send_khaterh(update: Updates):
    if not check_status():
        
        return
    k =bio_fackt_faz.khatere()
    
    res =random.choice(k)
    await update.reply(res)

   
    
@bot.on_message_updates(filters.is_group , filters.text)
async def add_filter(update: Updates):
    if not check_status():
        
        return
    # بررسی شروع پیام با "فیلتر:"
    if update.text.startswith("فیلتر:"):
        if not await update.is_admin(user_guid=update.author_guid):  # چک کردن دسترسی ادمین
            await update.reply("⛔ شما اجازه این کار را ندارید!")
            return

        # استخراج کلمه یا عبارت برای فیلتر
        phrase_to_filter = update.text.split("فیلتر:", 1)[1].strip()
        
        if phrase_to_filter:  # بررسی خالی نبودن عبارت
            filtered_phrases.add(phrase_to_filter)
            await update.reply(f"✅ عبارت '{phrase_to_filter}' به لیست فیلتر اضافه شد.")
        else:
            await update.reply("⚠️ لطفاً یک عبارت برای فیلتر کردن وارد کنید.")

# نمایش کلمات فیلترشده با فرمان "لیست_فیلتر"
@bot.on_message_updates(filters.is_group , filters.Commands(['لیست_فیلتر'], prefixes=''))
async def list_filtered_phrases(update: Updates):
    if not check_status():
        
        return
    if not await update.is_admin(user_guid=update.author_guid):  # چک کردن دسترسی ادمین
        await update.reply("⛔ شما اجازه این کار را ندارید!")
        return

    # نمایش کلمات فیلترشده
    if filtered_phrases:
        filtered_list = "\n".join([f"- {phrase}" for phrase in filtered_phrases])
        await update.reply(f"📜 لیست کلمات فیلتر شده:\n\n{filtered_list}")
    else:
        await update.reply("ℹ️ لیست فیلترها خالی است.")

# پاک‌سازی لیست فیلترها
@bot.on_message_updates(filters.is_group , filters.Commands(['پاک_لیست'], prefixes=''))
async def clear_filters(update: Updates):
    if not check_status():
        
        return
    if not await update.is_admin(user_guid=update.author_guid):
        await update.reply("⛔ شما اجازه این کار را ندارید!")
        return

    filtered_phrases.clear()
    await update.reply("🧹 لیست فیلترها پاک شد.")

# حذف پیام‌های حاوی کلمات فیلتر شده و محدود کردن کاربر
@bot.on_message_updates(filters.is_group , filters.text)
async def filter_messages(update: Updates):
    if not check_status():
        
        return
    if any(phrase in update.text for phrase in filtered_phrases):
        await update.delete_messages()  # حذف پیام
        
        await update.reply("⛔ پیام شما حاوی کلمات فیلتر شده بود و حذف شد.")
    
                    
@bot.on_message_updates(filters.is_group , filters.Commands(['پیش بینی','پیش_بینی','اینده_نگری'], prefixes=''))   
async def send_predictions(update: Updates):
    if not check_status():
        
        return
    prediction_keywords = re.compile(r"(پیش[ _-]*بینی|آینده[ _-]*نگری|طالع[ _-]*بینی)", re.IGNORECASE)
    category = random.choice(list(predictions.keys()))
    # انتخاب یک پیش‌بینی تصادفی از دسته انتخاب‌شده
    prediction = random.choice(predictions[category])
    if prediction_keywords.search(update.text):
        
    # ارسال پیش‌بینی به کاربر
        await update.reply(f"پیش‌بینی شما برای امروز (دسته: {category}):\n{prediction}")
    
        
        
        
            
@bot.on_message_updates(filters.is_group , filters.Commands(['ترفند','اموزش'], prefixes=''))
async def send_tarfand(update: Updates):
    if not check_status():
        
            
        return
    t =bio_fackt_faz.tips()
    res =random.choice(t)
    await update.reply(res) 
           
           
@bot.on_message_updates(filters.is_group , filters.Commands(['قیمت_پول','پول'], prefixes=''))
async def send_money(update: Updates):
    if not check_status():
        
            
        return
    response = requests.get("https://pybot.info/api/money.php")
    if response.status_code == 200 and response.json().get("ok"):
        await update.reply("درحال به دست اوردن قیمت ..")
        # Parse the JSON data
        data = response.json()["result"]
        
        # Extract and format the currency data
        message = (
            f"💵 قیمت  پول ها :\n\n"
            f"دلار: {data['dolar']} ریال\n"
            f"یورو: {data['euro']} ریال\n"
            f"پوند: {data['pond']} ریال\n"
            f"درهم: {data['derham']} ریال\n"
            f"لیر: {data['lir']} ریال\n"
            
        )
        
        
        await update.reply(message)
    else:
        await update.reply("❌ دریافت اطلاعات ارز با مشکل مواجه شد. لطفاً دوباره تلاش کنید.")


@bot.on_message_updates(filters.is_group)
async def chatbot_man(update: Updates):
    if not check_status():
        
            
        return
    user_message = update.text  # پیام دریافتی از کاربر
    chatbot_response = chatbot.respond(user_message)  # پاسخ از چت‌بات NLTK
    await update.reply(chatbot_response) 

@bot.on_message_updates(filters.is_group , filters.Commands(['بهداشتی','توصیه_بهداشتی'], prefixes=''))
async def send_health_tips(update: Updates):
    if not check_status():
        
            
        return
    category, tip = get_random_health_tip()
    await update.reply(f"🔹 توصیه بهداشتی امروز ({category}):\n{tip}")
    
    
@bot.on_message_updates(filters.is_group)
async def send_voice_man_and_wommen(update: Updates):
    if not check_status():
            
            
        return
    message_text = update.text.lower()
    
    # چک کردن نوع صدا براساس دستور ورودی
    if message_text.startswith("ویس مرد"):
        await update.reply("درحال پردازش وساخت ویس شما هستم لطفا کمی صبرکنید .....")
        text = message_text.replace("ویس مرد", "").strip()
        audio_path = fetch_audio(text, "male")
        
        if audio_path:
            await update.reply("الانه که ارسال بشه ویس مذکر شما")
            
            await update.reply_voice(audio_path,caption=f"متن تبدیل شده شما  به ویس مذکر \n{message_text}")
           
        else:
            await update.reply("خطایی در تولید فایل صوتی رخ داده است.")

    elif message_text.startswith("ویس زن"):
        text = message_text.replace("ویس زن", "").strip()
        audio_path = fetch_audio(text, "female")
        
        if audio_path:
            await update.reply("الانه که ارسال بشه ویس مونث شما ارسال شود.")
            await update.reply_voice(audio_path,caption=f"متن تبدیل شده شما به مونث :\n{message_text}")
        else:
            await update.reply("خطایی در تولید فایل صوتی رخ داده است.")
    
@bot.on_message_updates(filters.is_group)
async def handle_gender_commands(update: Updates):
    message_text = update.text.strip()
    if not check_status():
            
            
        return
    # اگر پیام با #مرد شروع می‌شود
    if message_text.startswith("#مرد"):
        await update.reply("🔄 در حال پردازش درخواست شما هستم... کمی شکیبا باشید لطفاً.")
        
        # حذف #مرد از متن و پردازش باقی‌مانده
        user_query = message_text.replace("#مرد", "").strip()
        
        # پردازش سوال
        chatbot_response = get_chatbot_response(user_query)
        if chatbot_response:
            await update.reply("صبرکنید تا براتون توضیحات را درویس بگم..")
            
            # تولید فایل صوتی پاسخ (صدای مردانه)
            audio_path = fetch_audio(chatbot_response, "male")
            if audio_path:
                await update.reply("**الان حاضرمیشه**")
                await update.reply_voice(audio_path, caption=f"پاسخ: {chatbot_response}")
                os.remove(audio_path)  # حذف فایل پس از ارسال
            else:
                await update.reply("خطایی در تولید فایل صوتی رخ داده است.")
        else:
            await update.reply("پاسخی یافت نشد.")
    
    # اگر پیام با #زن شروع می‌شود
    elif message_text.startswith("#زن"):
        await update.reply("🔄 در حال پردازش درخواست شما هستم... کمی شکیبا باشید لطفاً.")
        
        # حذف #زن از متن و پردازش باقی‌مانده
        user_query = message_text.replace("#زن", "").strip()
        
        # پردازش سوال
        chatbot_response = get_chatbot_response(user_query)
        if chatbot_response:
            await update.reply("صبرکنید تا براتون توضیحات را درویس بگم..")
            
            # تولید فایل صوتی پاسخ (صدای زنانه)
            audio_path = fetch_audio(chatbot_response, "female")
            if audio_path:
                await update.reply("**الان حاضرمیشه**")
                await update.reply_voice(audio_path, caption=f"پاسخ: {chatbot_response}")
                os.remove(audio_path)  # حذف فایل پس از ارسال
            else:
                await update.reply("خطایی در تولید فایل صوتی رخ داده است.")
        else:
            await update.reply("پاسخی یافت نشد.")

   
@bot.on_message_updates(filters.is_group , filters.Commands(['play'], prefixes='')) 
async def raundom_music(update: Updates):
    if not check_status():
            
            
        return
    guid =update.object_guid
    song_url = get_random_music_link()
    if song_url:
        await update.reply(f"🎶 آهنگ تصادفی شما:\n{song_url}")
        await bot.voice_chat_player(guid, song_url)
    else:
        await update.reply("آهنگی یافت نشد.")
@bot.on_message_updates(filters.is_group , filters.Commands(['music'], prefixes='')) 
async def send_music_ranudom(update: Updates):
    if not check_status():
            
            
        return
    song_url = get_random_music_link()
    if song_url:
        await update.reply(f"🎶 آهنگ تصادفی شما:\n{song_url}")
        await update.reply_music(song_url,caption=f"🎶 آهنگ تصادفی شما:\n{song_url}")
    else:
        await update.reply("آهنگی یافت نشد.")
    
    
@bot.on_message_updates(filters.is_group , filters.Commands(['حقیقت'], prefixes='')) 
async def send_haqiqt(update: Updates):
    if not check_status():
            
            
        return
    haqiqat_choice = random.choice(haqiqat)
    await update.reply(haqiqat_choice)
@bot.on_message_updates(filters.is_group , filters.Commands(['جرعت'], prefixes=''))
async def send_joret(update: Updates):
    if not check_status():
            
            
        return
    jorat_choice = random.choice(joraat)
    await update.reply(f"جرأت: {jorat_choice}") 
@bot.on_message_updates(filters.is_group , filters.Commands(['اشپزی','دستپخت'], prefixes='')) 
async def send_food(update: Updates):
    if not check_status():
            
            
        return
    food, category = bio_fackt_faz.suggest_food()
    
    await update.reply(f"🍽️ پیشنهاد ما: {food}\n📂 دسته‌بندی: {category}") 


@bot.on_message_updates(filters.is_group) 
async def send_bmi(update: Updates):
    if not check_status():
            
            
        return
    message_text = update.text
    if message_text.startswith("bmi:"):
        
        weight, height, error_message = validate_input(message_text)
        await update.reply("درحال پردازش bmiشما ...")

        if error_message:
            await update.reply(f"🚨 خطا: {error_message}\n\nنمونه فرمت: bmi:w=70,h=1.75")
            return

        bmi = calculate_bmi(weight, height)
        if bmi is None:
            await update.reply("🚫 خطا: ورودی نامعتبر. لطفاً دوباره تلاش کنید.")
            return

        advice = get_bmi_advice(bmi)
        
        # پاسخ زیبا و دقیق با استفاده از استایل HTML
        await update.reply(f"🔢 محاسبه BMI شما:\n\n"
                        f"✅ BMI: {bmi}\n\n"
                        f"📋 توصیه‌های پزشکی:\n\n"
                        f"{advice}\n\n"
                        f"📌 نکته: همیشه قبل از شروع هر برنامه ورزشی یا رژیم غذایی با یک پزشک مشورت کنید.")
        
@bot.on_message_updates(filters.is_group) 
async def send_tourist_spots(update: Updates):
    if not check_status():
            
            
        return
    if update.text.startswith("گردشگری:"):
        
        city = update.text.split(":")[1].strip()  # استخراج نام شهر از متن
        
        if city in tourist_spots:
            spots = '\n'.join(tourist_spots[city])
            await update.reply(f"مکان‌های دیدنی در {city}:\n{spots}")
        else:
            await update.reply("شهر وارد شده نامعتبر است. لطفاً نام یک شهر معتبر وارد کنید.")
    # دستور "لیست_شهر" برای نمایش شهرهای پشتیبانی شده
    elif update.text == "شهرها":
        available_cities = '\n'.join(tourist_spots.keys())
        await update.reply(f"شهرهای پشتیبانی شده:\n{available_cities}")
@bot.on_message_updates(filters.is_group , filters.Commands(['صلوات'], prefixes=''))  
async def send_salavat(update: Updates):
    if not check_status():
            
            
        return
    
    await update.reply("**اللّهُمَّ صَلِّ عَلَى مُحَمَّدٍ وَ آلِ مُحَمَّدٍ وَ عَجِّلْ فَرَجَهُمْ 🌸✨**")
    
@bot.on_message_updates(filters.is_group , filters.Commands(['دعا'], prefixes=''))
async def send_doeah(update: Updates):
    if not check_status():
            
            
        return
    duas=bio_fackt_faz.duse()
    dua = random.choice(duas)
    response = (
        "🌟 **دعای امروز** 🌟\n\n"
        f"📜 **عربی:** {dua['arabic']}\n"
        f"📖 **ترجمه:** {dua['persian']}"
    )
    await update.reply(response)
    
@bot.on_message_updates(filters.is_group)
async def lerneing_botgap(update: Updates):
    chat_id = update.author_guid
    sender_id = update.author_guid
    message = update.text.strip()
    if not check_status():
            
            
        return
    # مدیریت دستورات مخصوص مالک
    if sender_id == owners:
        if message.lower() == "یادگیری_فعال":
            set_learning_enabled(True)
            await update.reply("✅ حالت یادگیری فعال شد.")
            return
        elif message.lower() == "یادگیری_خاموش":
            set_learning_enabled(False)
            await update.reply("🚫 حالت یادگیری غیرفعال شد.")
            return
        elif message.lower() == "لیست_ذخیره":
            qa_list = get_all_questions_answers()
            if qa_list:
                response = "📋 **لیست سوالات و پاسخ‌ها:**\n\n"
                for idx, (question, answer) in enumerate(qa_list, 1):
                    response += f"{idx}. **سوال:** {question}\n   **پاسخ:** {answer}\n\n"
                await update.reply(response)
            else:
                await update.reply("⚠️ هیچ سوالی ذخیره نشده است.")
            return
        elif message.lower() == "پاک_یادگیری":
            clear_knowledge_base()
            await update.reply("🗑️ تمامی اطلاعات یادگیری پاک شدند.")
            return

    # بررسی وضعیت یادگیری
    learning_enabled = is_learning_enabled()

    # بررسی فرمت آموزش تک خطی (سوال=پاسخ)
    if "=" in message:
        parts = message.split("=", 1)
        if len(parts) == 2:
            question, answer = parts[0].strip(), parts[1].strip()
            if question and answer:
                if learning_enabled:
                    save_question_answer(question, answer)
                    await update.reply(f"✅ یاد گرفتم: **{question}** = **{answer}**")
                else:
                    await update.reply("🚫 حالت یادگیری غیرفعال است.")
            else:
                await update.reply("⚠️ فرمت صحیح نیست. باید به صورت `سوال=پاسخ` باشد.")
        else:
            await update.reply("⚠️ فرمت صحیح نیست.")
    else:
        # بررسی اگر سوال در دیتابیس موجود باشد
        answer = get_answer(message)
        if answer:
            await update.reply(answer)
        # اگر سوالی نباشد، هیچ پاسخی داده نمی‌شود
        else:
            pass  # هیچ پاسخی داده نمی‌شود
        
@bot.on_message_updates(filters.is_group)
async def send_loc(update: Updates):
    if not check_status():
            
            
        return
    if update.text.startswith("loc"):
        
        
        location_name = update.text.replace('loc','').strip()
        await update.reply("درحال پردازش مکان شما ...")
        
        # دریافت لینک گوگل مپس
        google_maps_url = get_location_map(location_name)
        
        
        # ارسال لینک به کاربر
        await update.reply(f"لینک مکان شما :\n{google_maps_url}")


@bot.on_message_updates(filters.is_group,filters.Commands(['pin','سنجاق'],prefixes=''))
async def pin_message_by_admin(update: Updates):
    
    group = update.object_guid  # GUID گروه
    if not check_status():
                
                
            return
    try:
        # بررسی اینکه کاربر ادمین است
        if group and await update.is_admin(user_guid=update.author_guid):
            # بررسی اینکه پیام ریپلای شده وجود دارد
            if update.reply_message_id:
                # سنجاق کردن پیام
                await update.client.set_pin(object_guid=group, message_id=update.reply_message_id)
                await update.reply("📌 پیام مورد نظر با موفقیت سنجاق شد.")
            else:
                await update.reply("🚫 لطفاً روی پیامی که می‌خواهید سنجاق شود ریپلای کنید.")
        else:
            await update.reply("🚫 فقط ادمین‌ها می‌توانند پیام‌ها را سنجاق کنند.")

    except exceptions.InvalidInput:
        await update.reply("🚫 خطایی در اطلاعات ورودی رخ داده است.")
    except Exception as e:
        await update.reply(f"🚫 خطایی غیرمنتظره رخ داد: {str(e)}")




@bot.on_message_updates(filters.is_group,filters.Commands(['شناسه اش','گویدش'],prefixes='')) 
async def get_guid_by_admin(update:Updates):
    group = update.object_guid  # GUID گروه
   
    if not check_status():
            
            
        return
    try:
        # بررسی اینکه کاربر ادمین است
        if group and await update.is_admin(user_guid=update.author_guid):
            # بررسی اینکه پیام ریپلای شده وجود دارد
            if update.reply_message_id:
                # دریافت پیام ریپلای‌شده
                replied_message = await update.get_messages(message_ids=update.reply_message_id)
                sender_guid = replied_message.messages[0].author_object_guid
                
                # ارسال شناسه GUID
                await update.reply(f"👤 شناسه GUID کاربر ریپلای‌شده: `{sender_guid}`")
            else:
                await update.reply("🚫 لطفاً روی پیامی که می‌خواهید GUID آن دریافت شود ریپلای کنید.")
        else:
            await update.reply("🚫 فقط ادمین‌ها می‌توانند این دستورات را اجرا کنند.")

    except exceptions.InvalidInput:
        await update.reply("🚫 خطایی در اطلاعات ورودی رخ داده است.")
    except Exception as e:
        await update.reply(f"🚫 خطایی غیرمنتظره رخ داد: {str(e)}")

@bot.on_message_updates(filters.is_group,filters.Commands(['چیستان'],prefixes=''))
async def send_chistan(update:Updates):
    if not check_status():
        
            
            
        return
    ch =bio_fackt_faz.riddles()
    random_riddle = random.choice(ch)
    await update.reply(f"چیستان: {random_riddle['question']}\n جواب: {random_riddle['answer']}")
@bot.on_message_updates(filters.is_group,filters.Commands(['علما','دانشمند'],prefixes='')) 
async def send_bozorgan_shia(update:Updates):
    if not check_status():
        
            
            
        return
    await update.reply("منتظرپاسخ باشید....")
    quote = get_random_quote()
    # ارسال پاسخ به کاربر
    await update.reply(quote)  

@bot.on_message_updates(filters.is_group)
async def generate_logo_ai(update: Updates):
    if not check_status():
        
            
            
        return
    if update.text.startswith("لگو"):
        
        await update.reply("درحال ساخت لگو از وب سرویس")
        # استخراج متن از پیام (بعد از "لوگو ")
        text = update.text[4:].strip()
        id = random.randint(1, 140)  # انتخاب تصادفی یک شناسه برای لوگو
        
        # ساخت URL درخواست برای تولید لوگو
        image_url = f"https://api.fast-creat.ir/logo?apikey=6285658042:kHq1WRiE3YeOKI5@Api_ManagerRoBot&type=logo&id={id}&text={text}"
        
        # ارسال درخواست با استفاده از requests
        response = requests.get(image_url)
        
        if response.status_code == 200:
            # ذخیره فایل تصویر لوگو در سیستم
            with open('logo.png', 'wb') as file:
                file.write(response.content)
            
            # ارسال عکس به گروه
            await bot.send_photo(update.object_guid, "logo.png", caption=f"لوگو شما آماده شد\n\n» متن لوگو: {text}", reply_to_message_id=update.message.message_id)
            
            # حذف فایل لوگو پس از ارسال
            os.remove("logo.png")
        else:
            # در صورت بروز مشکل، ارسال پیام خطا
            await update.reply("خطا در درخواست به وب.")

        


@bot.on_message_updates(filters.is_group)
async def join_chat_admin(update: Updates):
    if not check_status():
        
            
            
        return
    if update.author_guid == owners:
        # دستور join را فقط مالک می‌تواند اجرا کند
        if update.text.startswith("جوین:"):
            # دریافت لینک گروه
            group_link = update.message.text.replace("جوین:", "").strip()
            if group_link:
                try:
                    await bot.join_chat(group_link)
                    await update.reply("ربات با موفقیت عضو گروه شد.")
                except Exception as e:
                    await update.reply(f"خطا در عضویت در گروه: {e}")
            else:
                await update.reply("لینک گروه معتبر نیست. لطفا دوباره تلاش کنید.")
        elif update.text =="لفت":
            await bot.leave_group(update.object_guid)

@bot.on_message_updates(filters.is_private)
async def join_chat_admin(update: Updates):
    if not check_status():
        
            
            
        return
    if update.author_guid == owners:
        # دستور join را فقط مالک می‌تواند اجرا کند
        if update.text.startswith("جوین:"):
            # دریافت لینک گروه
            group_link = update.message.text.replace("جوین:", "").strip()
            if group_link:
                try:
                    await bot.join_chat(group_link)
                    await update.reply("ربات با موفقیت عضو گروه شد.")
                except Exception as e:
                    await update.reply(f"خطا در عضویت در گروه: {e}")
            else:
                await update.reply("لینک گروه معتبر نیست. لطفا دوباره تلاش کنید.")
        elif update.text =="لفت":
            await bot.leave_group(update.object_guid)
            
            
  
   
       

@bot.on_message_updates(filters.is_group,filters.Commands(['اسم گروه','اسم گپ'],prefixes=''))
async def get_name_gap(update: Updates):
    if not check_status():
            
            
            
        return
    gap =update.object_guid
    res =await bot.get_group_info(gap)
    data =res["group"]["group_title"]    
    await update.reply(data)
    
  
@bot.on_message_updates(filters.is_group)
async def search_myket_(update: Updates):
    if not check_status():
            
            
            
        return
    query = update.text
    if query.startswith('مایکت'):
        query =query.replace("مایکت","")
        await update.reply("در حال جستجو لطفا صبر کنید...")
        result = await search_myket(query)
        if result:
            # ارسال عکس و توضیحات به صورت کپشن (بدون فرمت HTML)
            caption = f"عنوان: {result['title']}\n"
            caption += f"لینک دانلود: {result['download']}\n"
            caption += f"لینک مایکت: {result['link']}"
            
            # ارسال عکس همراه با توضیحات (کپشن)
            await update.reply_photo(photo=result['photo'], caption=caption)
        else:
            await update.reply("❗ متاسفانه نتایجی پیدا نشد.")
      
    

    


@bot.on_message_updates(filters.text ,filters.is_group)
async def remove_user_chat(update: Updates):
    if not check_status():
            
            
            
        return
    group =update.object_guid
    
    if group and await update.is_admin(user_guid=update.author_guid):
        
        if update.text.startswith("ریم:@"):
            # استخراج نام کاربری از متن پیام
            username = update.text.split("@")[1].strip()

            try:
                # دریافت اطلاعات کاربر بر اساس نام کاربری
                user = await bot.get_object_by_username(username)
                
                if user:
                    # استخراج user_guid از اطلاعات کاربر
                    user_guid = user['user'].get('user_guid')
                    print(user_guid)
                    
                    if user_guid:
                        # حذف کاربر از گروه
                        await bot.ban_member(update.object_guid,user_guid)
                        await update.reply(f"کاربر @{username} با موفقیت ریمو شد.")
                    else:
                        await update.reply("شناسه کاربر یافت نشد.")
                else:
                    await update.reply("کاربر موردنظر یافت نشد.")
                    
            except Exception as e:
                await update.reply(f"مشکلی پیش آمد: {str(e)}")
@bot.on_message_updates(filters.is_group)
async def manage_admin(update: Updates):
    if not check_status():
            
            
            
        return
    group =update.object_guid
    if group and await update.is_admin(user_guid=update.author_guid):
        if update.text.startswith("ادمین:@"):
            # استخراج نام کاربری از متن پیام
            username = update.text.split("@")[1].strip()

            try:
                # دریافت اطلاعات کاربر بر اساس نام کاربری
                user = await bot.get_object_by_username(username)
                
                if user:
                    # استخراج user_guid از اطلاعات کاربر
                    user_guid = user['user'].get('user_guid')
                    print(f"User GUID: {user_guid}")
                    
                    if user_guid:
                        # اضافه کردن کاربر به عنوان مدیر با دسترسی محدود (فقط ارسال پیام)
                        group_guid = update.object_guid  # گروهی که پیام در آن ارسال شده
                        # دسترسی محدود به ارسال پیام
                        await bot.set_group_admin(group_guid, user_guid, action="SetAdmin")
                        await update.reply(f"کاربر @{username} با موفقیت به عنوان مدیر با دسترسی محدود تعیین شد.")
                    else:
                        await update.reply("شناسه کاربر یافت نشد.")
                else:
                    await update.reply("کاربر موردنظر یافت نشد.")
                    
            except Exception as e:
                await update.reply(f"مشکلی پیش آمد: {str(e)}")
        
        elif update.text.startswith("ادمین2:@"):
            # استخراج نام کاربری از متن پیام
            username = update.text.split("@")[1].strip()

            try:
                # دریافت اطلاعات کاربر بر اساس نام کاربری
                user = await bot.get_object_by_username(username)
                
                if user:
                    # استخراج user_guid از اطلاعات کاربر
                    user_guid = user['user'].get('user_guid')
                    print(f"User GUID: {user_guid}")
                    
                    if user_guid:
                        # اضافه کردن کاربر به عنوان مدیر با دسترسی کامل
                        group_guid = update.object_guid  # گروهی که پیام در آن ارسال شده
                        await bot.set_group_admin(group_guid, user_guid, action="SetAdmin")
                        await update.reply(f"کاربر @{username} با موفقیت به عنوان مدیر با دسترسی کامل تعیین شد.")
                    else:
                        await update.reply("شناسه کاربر یافت نشد.")
                else:
                    await update.reply("کاربر موردنظر یافت نشد.")
                    
            except Exception as e:
                await update.reply(f"مشکلی پیش آمد: {str(e)}")

        elif update.text.startswith("برکنار:@"):
            # استخراج نام کاربری از متن پیام
            username = update.text.split("@")[1].strip()

            try:
                # دریافت اطلاعات کاربر بر اساس نام کاربری
                user = await bot.get_object_by_username(username)
                
                if user:
                    # استخراج user_guid از اطلاعات کاربر
                    user_guid = user['user'].get('user_guid')
                    print(f"User GUID: {user_guid}")
                    
                    if user_guid:
                        # حذف کاربر از حالت مدیر
                        group_guid = update.object_guid  # گروهی که پیام در آن ارسال شده
                        await bot.set_group_admin(group_guid, user_guid, action="UnsetAdmin")
                        await update.reply(f"کاربر @{username} از حالت مدیر حذف شد.")
                    else:
                        await update.reply("شناسه کاربر یافت نشد.")
                else:
                    await update.reply("کاربر موردنظر یافت نشد.")
                    
            except Exception as e:
                await update.reply(f"مشکلی پیش آمد: {str(e)}")
    


@bot.on_message_updates(filters.is_group)
async def generate_image_from_text_rubino(update: Updates):
    if not check_status():
            
            
            
        return
    get_guid_user =await get_guid()
    if update.author_guid == owners:

        if update.text.startswith('روبینو'):
            input_image = update.text.replace('روبینو', '').strip()
            await update.reply("لطفاً کمی صبر کنید، در حال پردازش درخواست شما هستیم. 🙏")
            try:
                r = photo_ai(input_image, 'downloaded_image_ai.jpg')
                with open('downloaded_image_ai.jpg', 'rb') as photo:
                    await update.reply("الان ارسال میشه روبینو")
                    await rubino.add_picture(get_guid_user,'downloaded_image_ai.jpg',caption="ساخته شده با هوش مصنوعی ")
                    await update.reply("ارسال شد")
            except Exception as e:
                await update.reply(f"خطا: {e}")

        elif update.text.startswith("post"):
            user_text = update.text.replace('post', '').strip()
            await update.reply("لطفاً کمی صبر کنید، در حال پردازش درخواست شما هستیم. 🙏")
            try:
                # ارسال درخواست به وب‌سرویس
                url = f"https://api.api-code.ir/image-gen/?text={user_text}"
                response = requests.get(url)
                if response.status_code == 200:
                    data = response.json()
                    image_url = data['image_url']

                    # دانلود تصویر از URL
                    image_response = requests.get(image_url)
                    if image_response.status_code == 200:
                        image = Image.open(BytesIO(image_response.content))
                        image_path = f"{user_text}.png"
                        image.save(image_path)

                        # ارسال تصویر به کاربر
                        with open(image_path, 'rb') as photo:
                           await rubino.add_picture(get_guid_user,photo,caption="عکس شما توسط هوش مصنوعی ساخته شد")
                    else:
                        await update.reply('خطا در دانلود تصویر.')
                else:
                    await update.reply('خطا در دریافت URL تصویر.')
            except Exception as p:
                await update.reply(f"خطا: {p}")  


        
    
@bot.on_message_updates(filters.is_group)
async def check_bug_messages(update: Updates):
    text = update.text
    if not check_status():
            
            
            
        return
    # بررسی هر الگوی باگ در متن پیام
    for pattern in bug_patterns:
        if re.search(pattern, text):
            await update.delete_messages()  # حذف پیام باگ‌دار
            await update.ban_member()  # ریمو کردن کاربر از گروه
            await update.reply("🚨 پیام باگ‌دار شناسایی و کاربر حذف شد!")  # پیام هشدار
            break  # جلوگیری از چندین بررسی همزمان

bot.run()




    
    
          
# راه‌اندازی ربات               






