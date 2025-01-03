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

class MongoDB(object):
    
    def __init__(self, host, port, user, password, db_name, collection):
        self._client = MongoClient(f'mongodb://{user}:{password}@{host}:{port}')
        self._collection = self._client[db_name][collection]
    
    def create_user(self, user):
        try:
            if self._collection.find_one({"username": user.get('username')}) == None:
                self._collection.insert_one(user)
        except Exception as ex:
            print(ex)

    def get_all_users(self):
        try:
            data = self._collection.find()
            return data
        except Exception as ex:
            print(ex)
    
    def find_by_username(self, username):
        try:
            data = self._collection.find_one({"username": username})
            return data
        except Exception as ex:
            print(ex)

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


def save_participants_to_mongo(participants):
    db = MongoDB(db_name='parser', user='admin', password='password', collection='user', host='mongo', port=27017)            

    for user in participants:
        try:
            if user.username:
                username = user.username
            else:
                user.username = ""
        except:
            pass

        db.create_user(user)



groups = get_all_groups_from_chats(get_all_chats())

for group in groups:
    participants = get_all_participants(group)
    save_participants_to_mongo(participants)