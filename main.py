from telethon.sync import TelegramClient
from dotenv import load_dotenv

import csv
import os

from telethon.tl.functions.messages import GetDialogsRequest, GetHistoryRequest
from telethon.tl.types import InputPeerEmpty, PeerChannel

from pymongo import MongoClient

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

phone = os.environ.get("phone")
api_id = os.environ.get("api_id")
api_hash = os.environ.get("api_hash")

client = TelegramClient(phone, api_id, api_hash)

client.start()

def get_all_chats():
    
    chats = []
    last_date = None
    size_chats = 200

    result = client(GetDialogsRequest(
        offset_date=last_date,
        offset_id=0,
        offset_peer=InputPeerEmpty(),
        limit=size_chats,
        hash=0
    ))

    chats.extend(result.chats)

    return chats

def get_all_groups_from_chats(chats):

    groups = []

    for chat in chats:
        try:
            if chat.megagroup == True:
                groups.append(chat)
        except:
            continue

    return groups

def get_all_participants(group):

    all_participants = []
    
    try:
        all_participants = client.get_participants(group)
    except:
        pass

    return all_participants

def get_all_messages(group):
    
    all_messages = []
    offset_id = 0
    limit = 100
    total_messages = 0
    total_count_limit = 100

    while True:
        history = client(GetHistoryRequest(
            peer=group,
            offset_id=offset_id,
            offset_date=None,
            add_offset=0,
            limit=limit,
            max_id=0,
            min_id=0,
            hash=0
        ))
        if not history.messages:
            break
        messages = history.messages
        for message in messages:
            all_messages.append(message.message)
        offset_id = messages[len(messages) - 1].id
        if total_count_limit != 0 and total_messages >= total_count_limit:
            break

    return all_messages


groups = get_all_groups_from_chats(get_all_chats())

all_participants = []

for group in groups:
    all_participants.append(get_all_participants(group))
    
print('Сохраняем данные в файл...')
with open("members.csv","w",encoding='UTF-8') as f:
    writer = csv.writer(f,delimiter="|",lineterminator="\n")
    writer.writerow(['username','name'])
    for user in all_participants:
        try:
            if user.username:
                username= user.username
            else:
                username= ""
            if user.first_name:
                first_name= user.first_name
            else:
                first_name= ""
            if user.last_name:
                last_name= user.last_name
            else:
                last_name= ""
            name= (first_name + ' ' + last_name).strip()
            writer.writerow([username,name])
        except:
            pass