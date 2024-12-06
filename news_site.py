import requests
from bs4 import BeautifulSoup

# استفاده از requests.Session برای افزایش کارایی و سرعت
session = requests.Session()

# مجموعه برای ذخیره لینک‌ها (بدون تکرار)
saved_links = set()

# لیست برای ذخیره اخبار
news_links = []

# تعداد صفحات که می‌خواهید کرول کنید
pages_to_scrape = 5  # شما می‌توانید تعداد صفحات را تغییر دهید

# تابع برای دریافت اخبار
def fetch_latest_news():
    global news_links, saved_links

    # شروع کرول کردن اخبار
    for num in range(pages_to_scrape):
        url = f"https://shahraranews.ir/fa/section/ajax/117/{num}"

        response = session.get(url)

        # بررسی وضعیت درخواست
        if response.status_code != 200:
            print(f"خطا در دریافت صفحه {num + 1}")
            continue

        soup = BeautifulSoup(response.text, "html.parser")

        # جستجو برای اخبار
        for item in soup.find_all("a"):
            href = item.get("href")
            if href and "ajax" not in href and href not in saved_links:
                saved_links.add(href)  # افزودن لینک به مجموعه برای جلوگیری از تکرار

                # ساخت دیکشنری برای هر خبر
                news_item = {
                    "url": "https://shahraranews.ir" + href,
                    "title": item.text.strip(),
                    "page": num  # شماره صفحه برای ترتیب‌دهی
                }
                news_links.append(news_item)

    # مرتب‌سازی اخبار بر اساس صفحه (صفحات اولیه جدیدتر هستند)
    news_links = sorted(news_links, key=lambda x: x["page"], reverse=True)
    return news_links
