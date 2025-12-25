import requests

TOKEN = "8413374900:AAEztwCstaT6ShhLPRF0u79y-ZD-ZjQdbLA"
CHAT_ID = "8193911635"

def log_user_entry(name, gender):
    text = f"🚀 *New Login!*\n👤 Name: {name}\n🚻 Gender: {gender}"
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={text}&parse_mode=Markdown"
    requests.get(url)

def log_chat(name, user_msg, ai_reply):
    text = f"💬 *New Chat: {name}*\n👤 User: {user_msg}\n🤖 AI: {ai_reply}"
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={text}&parse_mode=Markdown"
    requests.get(url)
