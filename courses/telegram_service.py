"""
Telegram ئۇقتۇرۇش مۇلازىمىتى
ئوقۇغۇچىلارغا Telegram ئارقىلىق ئۇقتۇرۇش يوللايدۇ
"""
import requests
from django.conf import settings


def send_telegram_message(chat_id, message):
    """
    Telegram ئارقىلىق ئۇچۇر يوللايدۇ

    Args:
        chat_id: ئىشلەتكۈچىنىڭ Telegram ID سى
        message: يوللىنىدىغان ئۇچۇر

    Returns:
        bool: مۇۋەپپەقىيەتلىك يوللاندىمۇ
    """
    if not settings.TELEGRAM_ENABLED:
        return False

    if not chat_id:
        return False

    url = f'https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage'

    data = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'HTML',
    }

    try:
        response = requests.post(url, data=data, timeout=5)
        return response.status_code == 200
    except Exception as e:
        print(f'❌ Telegram خاتالىقى: {e}')
        return False


def send_enrollment_approved(user, course):
    """تىزىملىتىش تەستىقلانغاندا ئۇقتۇرۇش"""
    if not user.telegram_id or not user.telegram_id.isdigit():
        return False

    message = f"""
✅ <b>تىزىملىتىشىڭىز تەستىقلاندى!</b>

📚 كۇرس: <b>{course.title}</b>
👤 ئوقۇغۇچى: {user.full_name or user.username}

{'👨‍🏫 ئوقۇتقۇچى: ' + course.instructor.name if course.instructor else ''}

سىزنى كۇرسىمىزغا قارشى ئالىمىز! 🎉

— {settings.TELEGRAM_SITE_NAME if hasattr(settings, 'TELEGRAM_SITE_NAME') else 'Edraak Education'}
"""
    return send_telegram_message(user.telegram_id, message.strip())


def send_enrollment_rejected(user, course, reason=''):
    """تىزىملىتىش رەت قىلىنغاندا ئۇقتۇرۇش"""
    if not user.telegram_id or not user.telegram_id.isdigit():
        return False

    message = f"""
❌ <b>تىزىملىتىشىڭىز رەت قىلىندى</b>

📚 كۇرس: <b>{course.title}</b>
👤 ئوقۇغۇچى: {user.full_name or user.username}
{'📝 سەۋەب: ' + reason if reason else ''}

باشقا كۇرسلىرىمىزغا تىزىملىنىپ باققايسىز! 🙏

— {settings.TELEGRAM_SITE_NAME if hasattr(settings, 'TELEGRAM_SITE_NAME') else 'Edraak Education'}
"""
    return send_telegram_message(user.telegram_id, message.strip())


def send_new_message(user, sender_name, subject):
    """يېڭى ئۇچۇر كەلگەندە ئۇقتۇرۇش"""
    if not user.telegram_id or not user.telegram_id.isdigit():
        return False

    message = f"""
📬 <b>يېڭى ئۇچۇر كەلدى!</b>

👤 يوللىغۇچى: {sender_name}
📋 ماۋزۇ: {subject}

توربەتكە كىرىپ ئۇچۇرنى كۆرۈڭ. 💬
"""
    return send_telegram_message(user.telegram_id, message.strip())


def send_welcome_message(user):
    """يېڭى تىزىملانغاندا قارشى ئېلىش ئۇچۇرى"""
    if not user.telegram_id or not user.telegram_id.isdigit():
        return False

    message = f"""
👋 <b>خۇش كەلدىڭىز!</b>

{user.full_name or user.username}، Edraak Education غا تىزىملاندىڭىز!

📚 كۇرسلىرىمىزنى كۆرۈپ، ئۆزىڭىزگە ماس كۇرسنى تاللاڭ.

مۇۋەپپەقىيەتلىك ئوقۇش تىلەيمىز! 🎓
"""
    return send_telegram_message(user.telegram_id, message.strip())