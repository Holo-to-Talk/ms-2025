import re

# バリデーション関数
def validate_name(name):
    if not name:
        return "駅名を入力してください。"
    return ""

def validate_station_num(station_num):
    if not station_num.encode('utf-8').isalnum():
        return "駅番号は半角英数字のみを入力してください。"
    if len(station_num) >= 6:
        return "駅番号は5文字以下で入力してください。"
    return ""

def validate_address(address):
    if not address:
        return "駅の住所を入力して下さい。"
    return ""

def validate_phone_num(phone_num):
    pattern = r"^\+?[0-9]{10,15}$"
    if not re.match(pattern, phone_num):
        return "電話番号が無効です。"
    return ""

def validate_twilio_twiml_app_sid(twilio_twiml_app_sid):
    if not twilio_twiml_app_sid.encode('utf-8').isalnum():
        return "twilio_twiml_app_sidは半角英数字のみを入力してください。"
    if len(twilio_twiml_app_sid) != 35:
        return "twilio_twiml_app_sidは半角英数字35文字です。"
    return ""

def validate_api_key(api_key):
    if not api_key.encode('utf-8').isalnum():
        return "api_keyは半角英数字のみを入力してください。"
    if len(api_key) != 35:
        return "api_keyは半角英数字35文字です。"
    return ""

def validate_api_secret(api_secret):
    if not api_secret.encode('utf-8').isalnum():
        return "api_secretは半角英数字のみを入力してください。"
    if len(api_secret) != 33:
        return "api_secretは半角英数字33文字です。"
    return ""

def validate_password(password):
    if len(password) < 5:
        return "パスワードは5文字以上で入力して下さい。"
    return ""