import requests

def chat_bot_response(user_message: str):
    """
    ارسال پیام کاربر به API چت‌بات و دریافت پاسخ.
    
    پارامترها:
        user_message (str): پیام کاربر به عنوان رشته‌ی ورودی.
        
    خروجی:
        str: پاسخ چت‌بات به صورت رشته.
    """
    try:
        # تنظیم URL و ارسال درخواست به API
        url = f"http://api.api-code.ir/api/ai-chatbot/?text={user_message}"
        response = requests.get(url)

        # بررسی وضعیت پاسخ API
        if response.status_code == 200:
            data = response.json()
            # بررسی وجود کلید "Result" در پاسخ API
            if "Result" in data:
                return data["Result"]
            else:
                return "پاسخی از API دریافت نشد."
        else:
            return f"خطا در اتصال به API: وضعیت {response.status_code}"

    except Exception as e:
        return f"یک خطای غیرمنتظره رخ داد: {e}"


def get_song(search_text: str):
    try:
        # ارسال درخواست به API برای جستجوی آهنگ
        url = f"https://api-free.ir/api/sr-music/?text={search_text}"
        response = requests.get(url)
        
        # بررسی وضعیت پاسخ API
        if response.status_code == 200:
            data = response.json()
            if data.get("ok") and "result" in data:
                return data["result"]  # عنوان و لینک آهنگ
            else:
                return {"error": "آهنگی یافت نشد یا مشکلی در پاسخ API وجود دارد."}
        else:
            return {"error": f"خطا در اتصال به API، کد وضعیت: {response.status_code}"}
            
    except Exception as e:
        return {"error": f"یک خطای غیرمنتظره رخ داد: {e}"}