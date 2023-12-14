import os
import subprocess
from datetime import datetime, timedelta

import pymongo
from dotenv import load_dotenv
import logging

from decorators import within_time_interval
from fakerSendSMS import send_sms

logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')

load_dotenv() 

MONGO_URL = os.getenv('MONGO_URL')
COLLECTION_SCRIPT = os.getenv('COLLECTION_SCRIPT')
START_DAY = os.getenv('START_DAY')
END_DAY = os.getenv('END_DAY')
DB_NAME = os.getenv('DB_NAME')
WORKING_SCRIPT = int(os.getenv('WORKING_SCRIPT'))


def get_db(db_name:str) -> pymongo.database.Database:
    client = pymongo.MongoClient(MONGO_URL)
    db = client[db_name]
    return db


def get_name_actual_colections() -> pymongo.cursor.Cursor:
    db = get_db(DB_NAME)
    collection = db[COLLECTION_SCRIPT]
    data_from = datetime.now() - timedelta(days=WORKING_SCRIPT)
    name_actual_collections = collection.find(
        {"created": {"$gte": data_from}})
   
    return name_actual_collections


@within_time_interval(start_time=START_DAY, end_time=END_DAY)
def sendAllSMS(db: pymongo.database.Database, collection_name: str) -> None:
    all_messages = db[collection_name].find(
        {DB_NAME: {"$exists": False}})
    for message in all_messages:
        response = send_sms('someurl',
                            data={'name': message.get('name'),
                                  'text': message['text'],
                                  'phone': message['phone']})
        id_sms = response.json().get('id')
        if response.status_code in [200, 201] and id_sms:
            db[collection_name].update_one(
                {'_id': message['_id']},
                {'$set': {DB_NAME: id_sms, 
                          'data_sent': datetime.now()}})
            logging.info(f"Message sent{message['name']}")
        else:
            logging.error(f"Message dont  sent{message['name']}")

   
def run_python_script(script_name: str) -> None:
    try:
        subprocess.run(["python", f"scripts/{script_name}"])
    except subprocess.CalledProcessError as e:
        message = f"Error in script {script_name}"
        logging.error(message)
        raise ValueError(message)        


@within_time_interval(start_time=START_DAY, end_time=END_DAY)
def run_python_script_in_interval(script_name: str) -> None:
    run_python_script(script_name)


def sendSMS() -> None:
    db = get_db(DB_NAME)
    collections = get_name_actual_colections()
    for coll in collections:
        sendAllSMS(db, coll.get('name'))


def run_all_scripts() -> None:
    collections = get_name_actual_colections()
    for coll in collections:
        run_python_script(coll.get('name'))
