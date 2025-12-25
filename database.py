# database.py
import datetime

def log_user_entry(name, gender):
    with open("logs.txt", "a", encoding="utf-8") as f:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"\n[NEW LOGIN] {timestamp} | Name: {name} | Gender: {gender}\n" + "-"*30)

def log_chat(name, user_msg, ai_reply):
    with open("logs.txt", "a", encoding="utf-8") as f:
        f.write(f"\n{name}: {user_msg}\nAI: {ai_reply}\n")
