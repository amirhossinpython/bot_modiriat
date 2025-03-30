import phonenumbers
from phonenumbers import geocoder, carrier, timezone, NumberParseException, PhoneNumberType



# تابع برای استخراج اطلاعات شماره تلفن
def get_phone_info(phone_number: str):
    try:
        # Parse کردن شماره تلفن
        parsed_number = phonenumbers.parse(phone_number)
        
        # اعتبارسنجی شماره
        is_valid = phonenumbers.is_valid_number(parsed_number)
        is_possible = phonenumbers.is_possible_number(parsed_number)
        
        # دریافت کشور و منطقه جغرافیایی
        country = geocoder.description_for_number(parsed_number, 'fa')
        
        # دریافت منطقه زمانی
        timezones = timezone.time_zones_for_number(parsed_number)
        
        # دریافت شرکت ارائه دهنده خدمات (اپراتور)
        operator = carrier.name_for_number(parsed_number, 'fa')
        
        # نوع شماره (موبایل، ثابت، یا VOIP)
        number_type = phonenumbers.number_type(parsed_number)
        if number_type == PhoneNumberType.MOBILE:
            number_type_str = "📱 موبایل"
        elif number_type == PhoneNumberType.FIXED_LINE:
            number_type_str = "☎️ ثابت"
        elif number_type == PhoneNumberType.VOIP:
            number_type_str = "🌐 VOIP"
        else:
            number_type_str = "نامشخص"
        
        # وضعیت شماره (قالب بین‌المللی، قالب نشنال)
        formatted_international = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
        formatted_national = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.NATIONAL)
        
        # کد کشور شماره
        country_code = parsed_number.country_code
        
        # تهیه اطلاعات به صورت متن
        info = (
            f"**اطلاعات شماره تلفن:**\n\n"
            f"📞 **شماره:** {phone_number}\n"
            f"🌐 **قالب بین‌المللی:** {formatted_international}\n"
            f"🏠 **قالب نشنال:** {formatted_national}\n"
            f"✅ **اعتبار شماره:** {'معتبر' if is_valid else 'نامعتبر'}\n"
            f"🔍 **آیا امکان‌پذیر است؟** {'بله' if is_possible else 'خیر'}\n"
            f"🌍 **کشور:** {country}\n"
            f"🌎 **کد کشور:** {country_code}\n"
            f"⏰ **منطقه زمانی:** {', '.join(timezones)}\n"
            f"📡 **اپراتور:** {operator}\n"
            f"📱 **نوع شماره:** {number_type_str}\n"
        )
        
        return info
    except NumberParseException:
        return "⚠️ شماره وارد شده معتبر نیست یا فرمت آن نادرست است."
    except Exception as e:
        return f"⚠️ مشکلی در پردازش اطلاعات شماره رخ داد: {str(e)}"

# مدیریت پیام‌های شامل دستور "شم
