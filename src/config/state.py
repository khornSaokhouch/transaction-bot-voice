import os
import json

STATE_FILE = "subscribed_users.json"

def load_subscribed_users():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return set(json.load(f))
    return set()

def add_subscribed_user(chat_id):
    users = load_subscribed_users()
    users.add(chat_id)
    with open(STATE_FILE, 'w') as f:
        json.dump(list(users), f)

SUBSCRIBED_CHAT_IDS = load_subscribed_users()
USER_STATES = {}
