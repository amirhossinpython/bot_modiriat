import socket
import aiohttp
def get_ip_address(url):
    try:
        # حذف پیشوندهای غیرضروری مثل http:// یا https://
        if url.startswith("http://"):
            url = url[7:]
        elif url.startswith("https://"):
            url = url[8:]
        
        # گرفتن دامنه‌ی اصلی
        domain = url.split('/')[0]
        
        # استخراج آدرس IP دامنه
        ip_address = socket.gethostbyname(domain)
        return ip_address
    
    except socket.gaierror:
        return "آدرس IP یافت نشد. لطفاً آدرس سایت را بررسی کنید."


