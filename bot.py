import os
import subprocess
import sys
from datetime import datetime
import sqlite3
import re
import random
from chat_bot import chat_bot_response,get_song
import asyncio
import prayer_times
from PIL import Image
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import shutil
from io import BytesIO
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])
try:
    import rubpy
    from rubpy import Client, filters, utils
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

# ساخت بات
bot = Client(name='Ai_bot')

music_styles = [
    "1- Pop 🎉", "2- Intense 🔥", "3- Violin 🎻", "4- Anthemic 🎺", 
    "5- Male Voice 👨‍🎤", "6- Funk 🎵", "7- Ethereal 🌌", 
    "8- Hard Rock 🤘", "9- Groovy 🎸", "10- Soul 🎷", 
    "11- Psychedelic 🌈", "12- Catchy 🎶", "13- Male Vocals 🎤", 
    "14- Japanese 🇯🇵", "15- Ambient 🌌", "16- Atmospheric ☁️", 
    "17- Synth 🎹", "18- Dreamy 🌙", "19- Electric Guitar 🎸"
]
help_ = """
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
از * هم میتونید استفاده کنید برای چت با هوش مصنوعی مثال ها :
+سلام
/سلام
✨ قابلیت ساخت تصویر:
برای ساخت تصویر کافیه دستور تصویر رو به همراه توضیحات ارسال کنید. برای مثال:

تصویر سلام
image man






"""

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




# دیکشنری برای نگهداری اخطارهای کاربران
warnings = {}
# دیکشنری جملات احوال‌پرسی و مکالمه‌های محاوره‌ای فارسی به ترکی (با حروف فارسی)


# تست برنامه



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
LINK_REGEX = r"(https?://\S+|www\.\S+)"  # حذف حساسیت به شناسه‌های کاربری


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

photo_lock = False
gif_lock =False
text_lock = False
voice_lock=False
user_data = {}
is_reporting = {}
GROUP_GUID='guid'
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
        is_admin = await update.is_admin(chat_id, user_id)  # استفاده از await برای فراخوانی متد

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
    group = update.object_guid
    
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






@bot.on_message_updates(filters.is_group,filters.Commands(['دستورات','help'],prefixes=''))  
def send_command(update: Updates)   :
    

        
    update.reply(help_)
       
       
      
@bot.on_message_updates(filters.voice,filters.is_group)     
def handle_voice_message(update: Updates):
    
    if voice_lock :
        update.delete()
        update.reply("پیام های حاوی ویس پاک میشن")
            
            
            
    



   


    
    
    
@bot.on_message_updates(filters.is_group)
def handle_message_text(update: Updates):
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
    
                
    
    
    if re.search(r'\bسلام\b', update.text.lower()):
        update.reply(greeting_message)

  

    # 3. پاسخ به پیام‌هایی که با "ربات" یا "میربات" شروع می‌شوند
    if re.match(r'^(ربات||بات)', update.text.lower()):
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
            
    
                
                   

     


@bot.on_message_updates(filters.is_group, filters.Commands(['لینک', 'link'], ''))
def send_group_link(update: Updates): 
    group = update.object_guid
    if group:
        link = bot.get_group_link(update.object_guid)
        return  update.reply(f' بفرماید لینک گروه\n{link.join_link}')
    


    
# هندلر برای دریافت سبک و متن آهنگ
@bot.on_message_updates(filters.Commands(['موزیک'],prefixes=''), filters.is_group)
async def music(update: Updates):
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
        
        
@bot.on_message_updates(filters.is_group,filters.Commands(['قفل'], prefixes=''))
async def lock_group(update: Updates):
    group = update.object_guid
    if group and await update.is_admin(user_guid=update.author_guid):
    
        await bot.set_group_default_access(
            group_guid=group,
            access_list=[]  # حذف دسترسی ارسال پیام
        )
        await update.reply("✅ گروه قفل شد. کاربران نمی‌توانند پیام ارسال کنند.")
    
@bot.on_message_updates(filters.is_group , filters.Commands(['باز'], prefixes=''))
async def unlock_group(update: Updates):
    group = update.object_guid
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
            



@bot.on_message_updates(filters.text,filters.is_group)
async def send_music_gapp(update: Updates):
    user_message = update.text.strip()
    
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
    user_message = update.text.strip()
    guid =update.object_guid
    # بررسی شروع پیام با "سرچ"
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

@bot.on_message_updates(filters.is_group)
def prayer_timess(message: Updates):
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
            
@bot.on_message_updates(filters.is_group,filters.Commands(['fal','فال'],prefixes=''))
def get_fal_and_send(update: Updates):
    update.reply("**منتظربمانید تابرایتان فال را اماد کنم**")
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
bot.run()
