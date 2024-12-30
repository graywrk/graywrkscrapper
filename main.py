from telethon.sync import TelegramClient
from dotenv import load_dotenv

import csv
import os

from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

phone = os.environ.get("phone")
api_id = os.environ.get("api_id")
api_hash = os.environ.get("api_hash")

client = TelegramClient(phone, api_id, api_hash)

client.start()

chats = []
last_date = None
size_chats = 200
groups = []

result = client(GetDialogsRequest(
    offset_date=last_date,
    offset_id=0,
    offset_peer=InputPeerEmpty(),
    limit=size_chats,
    hash=0
))

chats.extend(result.chats)

for chat in chats:
    try:
        if chat.megagroup == True:
            groups.append(chat)
    except:
        continue

print('Выберите номер группы из перечня:')
i=0
for g in groups:
   print(str(i) + '- ' + g.title)
   i+=1

g_index = input("Введите нужную цифру: ")
target_group=groups[int(g_index)]

print('Узнаём пользователей...')
all_participants = []
all_participants = client.get_participants(target_group)
 
print('Сохраняем данные в файл...')
with open("members.csv","w",encoding='UTF-8') as f:
   writer = csv.writer(f,delimiter=",",lineterminator="\n")
   writer.writerow(['username','name','group'])
   for user in all_participants:
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
       writer.writerow([username,name,target_group.title])     
print('Парсинг участников группы успешно выполнен.')

