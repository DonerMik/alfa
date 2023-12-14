import os
from random import randint

from dotenv import load_dotenv
from faker import Faker
from pymongo import MongoClient

load_dotenv() 

MONGO_URL = os.getenv('MONGO_URL')
COLLECTION_SCRIPTS  = os.getenv('COLLECTION_SCRIPTS ')
DB_NAME = os.getenv('DB_NAME')
NAME_SCRIPT = 'example_script.py'

client = MongoClient(MONGO_URL)
db = client[DB_NAME]

fake = Faker()

def create_tasks_sms(db: MongoClient, collection_name:str) -> None:
    docs = []
    for _ in range(randint(0, 20)):
        data = {'name': fake.name(),
                'text': fake.text(), 
                'phone': fake.phone_number()}
        docs.append(data)
    if not docs:
        return
    collection_to = db[collection_name]
    collection_to.insert_many(docs)


if __name__ == '__main__': 
    create_tasks_sms(db, NAME_SCRIPT)
    