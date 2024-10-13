import os
import subprocess
import sys
from datetime import datetime
from PIL import Image
import shutil
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])
try:
    import rubpy
    from rubpy import Client, filters, utils
    from rubpy.types import Updates
except ImportError:
    install('rubpy')
    import rubpy
    from rubpy import Client, filters, utils, exceptions
    from rubpy.types import Updates

try:
    import requests
except ImportError:
    install('requests')
    import requests
try:
    from pyowm import OWM
except ImportError:
    install('pyowm')
try:
    from gtts import gTTS
except ImportError:
    install("gtts")
    from gtts import gTTS
try :
    from khayyam import JalaliDatetime
except ImportError :
    install("khayyam")
    
    
import re
import random
# ساخت بات
bot = Client(name='Ai_bot')

help_="""

سلام!
ربات مدیریت گپ فعال شد و با امکانات جدید آماده است تا به بهتر شدن فضای گروه کمک کنه. بیایید یه نگاهی به قابلیت‌های جدید ربات بندازیم:

✨ ویژگی‌های ربات:

اخطار به کاربران:
هر کاربری که قوانین گروه رو نقض کنه، می‌تونید با ریپلای کردن روی پیامش بهش اخطار بدید. با رسیدن تعداد اخطارها به ۴ بار، کاربر به‌صورت خودکار از گروه حذف میشه.

کنترل لینک و آی‌دی:
اگر کسی لینک یا آی‌دی ارسال کنه، اخطار دریافت می‌کنه و با ۴ اخطار، کاربر از گروه حذف خواهد شد.

حذف یا بن کردن کاربران:
برای حذف یا بن کردن مستقیم، روی پیام کاربر ریپلای کنید و یکی از دستورات زیر رو وارد کنید:

بن
ریم
اخراج
قفل کردن محتوا:
ربات می‌تونه ارسال متن، عکس، گیف و ویس رو هم قفل کنه. یعنی در مواقع ضروری، امکان ارسال این نوع محتواها محدود میشه تا گروه منظم‌تر بمونه.

قابلیت چت با هوش مصنوعی:
با استفاده از این ربات، می‌تونید با هوش مصنوعی هم گفت‌وگو کنید. برای استفاده از این قابلیت، کافیه قبل از متن خودتون علامت + رو قرار بدید. ربات پیام شما رو پردازش کرده و پاسخ می‌ده.

ساخت تصویر:
برای ساخت تصویر کافیه دستور تصویر رو به همراه توضیحات ارسال کنید. برای مثال:


تصویر سلام
تولید ویس:
برای تولید ویس هم از دستور voice استفاده کنید. متنی که می‌خواید تبدیل به صدا بشه رو بعد از voice وارد کنید. برای مثال:


voice hi
قابلیت گرفتن وضعیت هوا:
برای دریافت وضعیت هوا کافیه دستور هوا رو به همراه نام شهر ارسال کنید. برای مثال:

هوا:Mashhad

"""


# دیکشنری برای نگهداری اخطارهای کاربران
warnings = {}

# حداکثر تعداد اخطار قبل از حذف
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
        "سلام و آرزوی بهترین‌ها برای شما!"
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
        "مرسی، شما چطورید؟"
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
        "هرگونه کمکی که نیاز دارید، بنده در خدمت هستم."
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
        "قابلی نداشت، هر زمان نیاز بود در خدمتم."
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
        "چرا کتاب‌های ریاضی همیشه ناراحتند؟ چون پر از مسائل حل‌نشده هستند.",
        "چرا ماهی‌ها حرف نمی‌زنند؟ چون همیشه در آب هستند و صداشان به گوش نمی‌رسد!",
        "چرا درختان همیشه خوشحالند؟ چون ریشه‌های محکمی دارند.",
        "یک کتاب با چه چیزی رابطه خوبی برقرار می‌کند؟ با یک خواننده خوب!",
        "چرا مداد همیشه از پاک‌کن تشکر می‌کند؟ چون هر اشتباهش را پاک می‌کند.",
        "چرا زنبورها همیشه مشغول کارند؟ چون می‌خواهند عسل خوشمزه درست کنند.",
        "چرا ساعت‌ها همیشه در حال دویدن هستند؟ چون زمان هرگز منتظر نمی‌ماند!",
        "چرا ابرها همیشه در حرکتند؟ چون نمی‌خواهند سر جایشان بمانند.",
        "چرا کفشدوزک‌ها همیشه به آرامی پرواز می‌کنند؟ چون نمی‌خواهند کسی را آزار دهند.",
        "چرا چراغ‌ها همیشه روشن می‌مانند؟ چون می‌خواهند مسیر را برای دیگران روشن کنند.",
        "چرا قورباغه‌ها همیشه در آب هستند؟ چون در آب خوشحال‌تر هستند.",
        "چرا کبوترها همیشه در حال پروازند؟ چون دوست دارند به آسمان نزدیک باشند.",
        "چرا خورشید همیشه می‌درخشد؟ چون می‌خواهد به دنیا نور بدهد.",
        "چرا گل‌ها همیشه به سمت خورشید می‌چرخند؟ چون از نور خورشید انرژی می‌گیرند.",
        "چرا ماه همیشه آرام است؟ چون به آرامی در آسمان حرکت می‌کند.",
        "چرا زمین همیشه محکم است؟ چون به ما استحکام و پشتیبانی می‌دهد.",
        "چرا ستاره‌ها شب‌ها می‌درخشند؟ چون می‌خواهند شب‌های ما را زیبا کنند.",
        "چرا پرندگان همیشه آواز می‌خوانند؟ چون دوست دارند شادی را به همه منتقل کنند.",
        "چرا گربه‌ها همیشه نرم هستند؟ چون می‌خواهند ما را آرام کنند.",
        "چرا خرس‌ها زمستان خوابند؟ چون دوست دارند در هوای سرد استراحت کنند."
        "چرا مرغ از خیابان رد شد؟ چون اون سمت خیابان مرغ کبابی بود!",
        "چرا دوچرخه نمی‌تونه سرپا بمونه؟ چون خیلی خسته است!",
        "چرا دیوار همیشه صحبت می‌کنه؟ چون گوشه‌داره!",
        "چرا کامپیوتر ناراحت شد؟ چون کلیکش شکسته بود!",
        ""
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
        "همه چیز به خوبی پیش می‌رود، شما چه خبر دارید؟"
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
        "هر زمان نیاز داشتید، من آماده پاسخگویی هستم."
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
        "با آرزوی موفقیت، خدانگهدار."
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
        "دعای خیر برای سلامتی شما و امام زمان (عج) را فراموش نکنید."
    ]
}

# الگوی شناسایی لینک و آیدی تلگرام
LINK_REGEX = r"(https?://\S+|www\.\S+|@[\w_]+)"
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
# خواندن کلمات از فایل متنی
bad_words = read_bad_words("bad_words.txt")
bad_patterns = create_patterns(bad_words)
photo_lock = False
gif_lock =False
text_lock = False
voice_lock=False

GROUP_GUID='محل گوید گروه'
# تابع بررسی اینکه آیا کاربر ادمین است یا نه
MEMBERS_PER_MESSAGE = 50

# تابع مدیریت پیام‌ها
@bot.on_message_updates(filters.is_group)
async def updates(update: Updates):
    print(updates)
    print(update)
    user_id = update.author_guid  # شناسه کاربر فرستنده پیام
    message_text = update.text  # متن پیام
    chat_id = update.object_guid  # شناسه گروه

    

        # شناسایی لینک یا آیدی در پیام
    if re.search(LINK_REGEX, message_text):
        # بررسی اینکه کاربر ادمین است یا نه
        is_admin = await update.is_admin(GROUP_GUID, user_id)  # استفاده از await برای فراخوانی متد

        if is_admin:
            # اگر کاربر ادمین باشد، لینک مجاز است
            await update.reply("✅ شما ادمین هستید و مجاز به ارسال لینک.")
        else:
            # اگر کاربر ادمین نباشد، لینک را شناسایی کرده و اخطار می‌دهد
            if user_id in warnings:
                warnings[user_id] += 1
            else:
                warnings[user_id] = 1

            await update.reply(f"🚫 شما مجاز به ارسال لینک نیستید! این {warnings[user_id]}مین اخطار شماست.")
            await update.delete_messages()  # حذف پیام

            # اگر تعداد اخطارها از حد مجاز بیشتر شد، کاربر را حذف می‌کنیم
            if warnings[user_id] >= MAX_WARNINGS:
                await update.reply("🚨 شما به دلیل ارسال مکرر لینک، از گروه حذف می‌شوید.")
                await update.ban_member()  # حذف یا بن کردن کاربر
                del warnings[user_id]  # پاک کردن رکورد کاربر پس از حذف






@bot.on_message_updates(filters.is_group, filters.Commands(['اخطار', 'رعایت'], prefixes=''))
async def warn_or_ban_user_by_admin(update: Updates):
    group = update.object_guid
   
        
    try:
        if group and update.is_admin(user_guid=update.author_guid):  # بررسی اینکه کاربر ادمین است
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
    
        
    if contains_prohibited_word(update.text, bad_patterns):
        a=await update.delete_messages()
        print(f"text :\n{update.text}\ndeleted:\n {a} ")
        messages = [
    "پیام شما به دلیل محتوای توهین‌آمیز حذف شد. لطفاً از زبان محترمانه استفاده کنید.",
    "شما اجازه ارسال پیام‌های توهین‌آمیز را ندارید. از رفتار محترمانه پیروی کنید.",
    "پیام شما حاوی الفاظ ناشایست بود و پاک شد. ادامه چنین رفتاری منجر به اقدامات شدیدتری خواهد شد.",
    "از شما درخواست می‌شود از ارسال پیام‌های توهین‌آمیز خودداری کنید، در غیر این صورت حساب کاربری شما مسدود خواهد شد.",
    "پیام‌های فحاشی و توهین‌آمیز خلاف قوانین است. لطفاً از ادبیات مناسب استفاده کنید.",
    "پیام شما به دلیل استفاده از کلمات ناپسند حذف شد. این رفتار قابل قبول نیست.",
    "به دلیل ارسال پیام‌های حاوی الفاظ نامناسب، پیام شما پاک شد. برای ادامه استفاده از پلتفرم، ادب و احترام را رعایت کنید.",
    "لطفاً از ارسال فحش و توهین به دیگران خودداری کنید. در صورت تکرار، دسترسی شما محدود خواهد شد.",
    "رفتار شما نامناسب است و پیام شما به دلیل محتوای غیر اخلاقی حذف شد. از ادبیات محترمانه استفاده کنید.",
    "هشدار: ارسال پیام‌های حاوی فحش و توهین منجر به محدودیت یا مسدود شدن حساب کاربری شما خواهد شد.",
    "بیشعور نباشید، فحاشی نکنید. این کار خلاف اخلاق و احترام است.",
    "فحاشی گناه است! بهتر است از کلمات مناسب و محترمانه استفاده کنید.",
    "لطفاً از ادبیات توهین‌آمیز خودداری کنید. این رفتار شما پذیرفتنی نیست.",
    "بس کنید! فحاشی باعث رنجش دیگران می‌شود. به دیگران احترام بگذارید.",
    "بی‌ادبانه فحش ندهید. پیام‌های شما پاک می‌شود و ممکن است مسدود شوید.",
    "این آخرین هشدار است! فحاشی و توهین ادامه یابد، دسترسی شما محدود خواهد شد.",
    "بجای فحاشی، از گفتگوهای سازنده استفاده کنید. ادب کلید ارتباطات موفق است.",
    "گناه است که با زبان خود دیگران را آزار دهید. پیام‌های توهین‌آمیز ممنوع است.",
    "حواستان به گفتارتان باشد! فحاشی و الفاظ زشت فقط شما را از دیگران دورتر می‌کند.",
    "بس کنید، این نوع صحبت باعث ناراحتی دیگران می‌شود. ادب را رعایت کنید."
]
        f =random.choice(messages)
        

        await update.reply(f)
    elif any(update.text.startswith(emoji) for emoji in ['🍆', '🌈', '🏳️‍🌈', '💧', '🍌', '🍑']):
        a = await update.delete_messages()

        
@bot.on_message_updates(filters.is_group, filters.Commands(["اعضا"]))
async def get_all_members(update: Updates):
    if update.object_guid == GROUP_GUID:
        
    
            
        if update.text == "/اعضا":
            try:
                has_continue = True
                next_start_id = None
                count = 1
                all_members = []

                while has_continue:
                    # دریافت اعضای گروه به صورت دسته‌ای
                    result = await bot.get_members(object_guid=GROUP_GUID, start_id=next_start_id)
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
        
                
@bot.on_message_updates(filters.Commands(["قفل_عکس", "باز_کردن_عکس","باز_کردن_متن","قفل_متن","قفل_گیف","باز_کردن_گیف",'قفل_ویس',"بازکردن_ویس"]),filters.is_group)
def toggle_locks(update: Updates):
    global photo_lock
    global text_lock
    global  gif_lock
    global voice_lock
   
    
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
  
    if photo_lock:
        # حذف پیام عکس
        update.delete()
        # ارسال پیام اطلاع‌رسانی
        update.reply("عکس‌ها در حال حاضر قفل هستند و پاک شدند.")

@bot.on_message_updates(filters.text,filters.is_group)
def handle_text_message(update: Updates):
    global text_lock
    
        
    if text_lock:
        # حذف پیام متنی
        update.delete_messages()
        # ارسال پیام اطلاع‌رسانی
        update.reply("پیام‌های متنی در حال حاضر قفل هستند و پاک شدند.")
        



   

@bot.on_message_updates(filters.gif,filters.is_group)
def handle_gif_message(update: Updates):
    global gif_lock
    
    if gif_lock:
        update.delete()
        update.reply("پیام های حاوی گیف پاک میشوند")






@bot.on_message_updates(filters.is_group,filters.Commands(['دستورات','help']))  
def send_command(update: Updates)   :
    
        
    update.reply(help_)
       
       
      
@bot.on_message_updates(filters.voice,filters.is_group)     
def handle_voice_message(update: Updates):
    
    if voice_lock :
        update.delete()
        update.reply("پیام های حاوی ویس پاک میشن")
            
            
            
    



   

@bot.on_message_updates(filters.is_group,filters.Commands(["create_poll","نظرسنجی","نظر"]))
def create_poll(update: Updates):
    
    question = "نظر شما درباره کیفیت خدمات ما چیست؟"
    options = ["عالی", "خوب", "متوسط", "ضعیف"]
    try:
        # ایجاد نظرسنجی
        poll = bot.create_poll(
            object_guid=GROUP_GUID,
            question=question,
            options=options,
            is_anonymous=False,
            allows_multiple_answers=False
        )

        # ارسال پیام تایید
        bot.send_message(GROUP_GUID, f'نظرسنجی با موفقیت ایجاد شد: {poll}')
       
    except Exception as e:
        bot.send_message(GROUP_GUID, f'خطا در ایجاد نظرسنجی: {str(e)}')
    
    
    
@bot.on_message_updates(filters.is_group)
def handle_message_text(update: Updates):
    greeting_message = random.choice(responses_dict['greetings'])
    if update.text.startswith('+'):
        update.reply("لطفاً کمی صبر کنید، در حال پردازش درخواست شما هستیم. ممکن است به دلیل تأخیر در وب‌سرویس زمان بیشتری طول بکشد. از شکیبایی شما سپاسگزاریم! 🙏")
        user_input = update.text[1:].strip()  # متن بدون "+"
        api_response = chatgpt(user_input)
        update.reply(api_response)
        return  
    
    
    if re.search(r'\bسلام\b', update.text.lower()):
        update.reply(greeting_message)

    # 2. پاسخ به پیام‌هایی که شامل "خوبی" و "ربات" یا مشابه آن هستند
    if re.search(r'(خوبی.*(ربات|بات|میربات))|(ربات.*خوبی)', update.text.lower()):
        update.reply(random.choice(responses_dict['how_are_you']))

    # 3. پاسخ به پیام‌هایی که با "ربات" یا "میربات" شروع می‌شوند
    if re.match(r'^(ربات|میربات|بات)', update.text.lower()):
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
            

        

     
@bot.on_message_updates(filters.is_group)
def send_voice_ai(update: Updates):
    if update.text and update.text.startswith('voice'):
        try:
            # دریافت محتوای بعد از "voice"
            voice_text = update.text[6:].strip()  # حذف کلمه "voice" و فاصله‌ها

            if voice_text:  # بررسی اینکه محتوای متنی بعد از "voice" وجود دارد
                update.reply("در حال ساخت ویس...")

                # پردازش ویس با محتوای دریافت شده
                rs = processing_voice(voice_text, 'voice.mp3')

                # ارسال فایل صوتی
                with open("voice.mp3", 'rb') as voice_file:
                    update.reply_voice('voice.mp3', caption="ویس شما آماده شد")
       
        except Exception as e:
            update.reply(f"خطایی رخ داد: {str(e)}")   
        finally:
            if os.path.exists("voice.mp3"):
                os.remove("voice.mp3")


                
@bot.on_message_updates(filters.is_group)
def get_weather_info(update: Updates):
    owm = OWM('api_key')   #ایپی کی خود را بزارید
    mgr = owm.weather_manager()
    location=update.text.replace("هوا:","")
    
    if update.text.startswith("هوا:"):
        update.reply("درحال به دست اوردن اطلاعات اب وهوا")
        
        try:
            
            # دریافت اطلاعات فعلی آب و هوا بر اساس مکان
            observation = mgr.weather_at_place(location)
            w = observation.weather

            # استخراج اطلاعات مورد نیاز
            status = w.detailed_status
            temperature = w.temperature('celsius')
            humidity = w.humidity
            wind = w.wind()
            pressure = w.pressure['press']
            clouds = w.clouds
            rain = w.rain
            heat_index = w.heat_index

            # نمایش اطلاعات
            print(f'اطلاعات آب و هوا در {location}:')
            print(f'وضعیت: {status}')
            print(f"دمای فعلی: {temperature['temp']}°C (کمینه: {temperature['temp_min']}°C, بیشینه: {temperature['temp_max']}°C)")
            print(f'رطوبت: {humidity}%')
            print(f"باد: {wind['speed']} متر بر ثانیه، جهت: {wind['deg']} درجه")
            print(f'فشار هوا: {pressure} hPa')
            print(f'ابرها: {clouds}%')
            print(f'باران: {rain}')
            print(f'شاخص حرارت: {heat_index}')
            update.reply(f"اطلاعات آب و هوا در {location}: \n وضعیت: {status}\nباد: {wind['speed']} متر بر ثانیه، جهت: {wind['deg']} درجه\nفشار هوا: {pressure} hPa \n ابرها: {clouds}%'\n باران: {rain}'\n شاخص حرارت: {heat_index}")
            
        except NotADirectoryError:
            print(f'مکان "{location}" یافت نشد!')
        except AttributeError:
            print('خطا در دریافت اطلاعات آب و هوا.')
        except UnboundLocalError:
            print('کلید API نامعتبر است. لطفاً یک کلید API معتبر وارد کنید.')
        except Exception as p :
            update.reply(f"erorr:\n{p}")

           
 
@bot.on_message_updates(filters.is_group, filters.Commands(["تاریخ", "زمان"], prefixes=''))
def send_data(update: Updates):
    # زمان فعلی به شمسی
    current_time_jalali = JalaliDatetime.today().strftime("%A %d %B %Y")
    
    # زمان فعلی به میلادی
    current_time_gregorian = datetime.now().strftime("%A %d %B %Y")
    
    # ساخت متن خروجی به صورت یک رشته
    result = (
        f"تاریخ به شمسی:\n{current_time_jalali}\n"
        f"تاریخ به میلادی:\n{current_time_gregorian}"
    )

    # ارسال پیام به گروه
    update.reply(result)
    
    
    
    

                

   
# اجرای بات
bot.run()
