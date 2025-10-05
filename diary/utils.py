import requests

ESKIZ_EMAIL = "aza4kf@gmail.com"      # Eskiz login
ESKIZ_PASSWORD = "dLx9jwunc9U7zBRz3CgN6DWDI8c4oVBlWWxmSCUe"   # Eskiz parolingiz

def get_eskiz_token():
    url = "https://notify.eskiz.uz/api/auth/login"
    data = {"email": ESKIZ_EMAIL, "password": ESKIZ_PASSWORD}
    resp = requests.post(url, data=data)
    if resp.status_code == 200:
        return resp.json()["data"]["token"]
    return None


def send_sms(phone, message):
    token = get_eskiz_token()
    if not token:
        return False

    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "mobile_phone": phone,
        "message": message,
        "from": "4546",
    }

    resp = requests.post("https://notify.eskiz.uz/api/message/sms/send", data=data, headers=headers)
    return resp.status_code == 200
