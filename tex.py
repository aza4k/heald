# import requests

# # 1) Token olish
# login_url = "https://notify.eskiz.uz/api/auth/login"
# login_data = {
#     "email": "aza4kf@gmail.com",
#     "password": "dLx9jwunc9U7zBRz3CgN6DWDI8c4oVBlWWxmSCUe"
# }
# resp = requests.post(login_url, data=login_data)
# print("Login status:", resp.status_code, resp.text)
# if resp.status_code != 200:
#     raise Exception("Login failed")

# token = resp.json()["data"]["token"]
# print("Got token:", token)

# # 2) SMS yuborish
# sms_url = "https://notify.eskiz.uz/api/message/sms/send"
# headers = {
#     "Authorization": f"Bearer {token}"
# }
# sms_data = {
#     "mobile_phone": "998912618831",
#     "message": "Test SMS dari Eskiz API",
#     "from": "4546"
# }
# resp2 = requests.post(sms_url, headers=headers, data=sms_data)
# print("SMS status:", resp2.status_code, resp2.text)


import requests

# 1️⃣ Login orqali token olish
login_resp = requests.post("https://notify.eskiz.uz/api/auth/login", data={
    "email": "aza4kf@gmail.com",
    "password": "dLx9jwunc9U7zBRz3CgN6DWDI8c4oVBlWWxmSCUe"
})

token = login_resp.json()['data']['token']
print("Got token:", token)

# 2️⃣ Test SMS yuborish
headers = {
    "Authorization": f"Bearer {token}"
}

sms_data = {
    "mobile_phone": "998912618831",   # telefon raqam (+998 dan keyin 9...) formatda
    "message": "Bu Eskiz dan test",   # faqat shu 3 test matndan biri
    "from": "4546",                   # Eskiz test kanali
    "callback_url": "http://example.com/callback"
}

resp = requests.post("https://notify.eskiz.uz/api/message/sms/send", data=sms_data, headers=headers)
print("SMS status:", resp.status_code, resp.text)
