from logging.handlers import RotatingFileHandler
import os
import pathlib
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
import logging

from fastapi import FastAPI, File, UploadFile
from fastapi import HTTPException

from utils import get_db, run_all_scripts, sendSMS
from validators import check_validated_script


logging.basicConfig(filename='app.log', filemode='a', format='%(name)s - %(levelname)s - %(message)s')

file_handler = RotatingFileHandler('app.log', maxBytes=1e6, backupCount=5)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

logging.getLogger().addHandler(file_handler)


load_dotenv() 

MINUTES_INTERVAL = int(os.getenv('MINUTES_INTERVAL'))
DB_NAME = os.getenv('DB_NAME')
COLLECTION_SCRIPT = os.getenv('COLLECTION_SCRIPT')
START_DAY = os.getenv('START_DAY')
END_DAY = os.getenv('END_DAY')


app = FastAPI()
scheduler = BackgroundScheduler()


@app.on_event('startup')
def start():
    scheduler.add_job(run_all_scripts, 'interval', minutes=MINUTES_INTERVAL)
    scheduler.add_job(sendSMS, 'interval', minutes=MINUTES_INTERVAL)
    scheduler.start()
    logging.info('Start scheduler')


@app.on_event('shutdown')  
def shutdown():
    scheduler.shutdown()
    logging.info('Stop scheduler')


@app.post('/uploadfile/')
async def create_upload_file(file: UploadFile = File(...))-> dict:
    script_path = pathlib.Path(f'scripts/{file.filename}')
    contents = await file.read()
    with open(script_path, 'w', encoding='utf-8') as buffer:
        buffer.write(contents.decode('utf-8'))
    try:
        check_validated_script(file.filename)
    except Exception as e:
        script_path.unlink()
        logging.error(f'Script doesnt accepted. Error: {e}')
        raise HTTPException(status_code=400, detail=str(e))
    db = get_db(DB_NAME)
    collection = db[COLLECTION_SCRIPT]
    collection.insert_one({'name': file.filename, 
                           'created': datetime.now()})
    logging.info('Python script accepted')
    return {'info': 'Python script accepted'}
