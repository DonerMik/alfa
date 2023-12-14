import re
import os

from utils import get_db, run_python_script


COLLECTION_SCRIPT = os.getenv('COLLECTION_SCRIPT')
DB_NAME = os.getenv('DB_NAME')
FIELD_SENT_SMS_ID = os.getenv('FIELD_SENT_SMS_ID')

def phone_must_match_pattern(v:str) -> None:
    pattern = r'^\+?1?\d{9,15}$'
    if not re.match(pattern, v):
        raise ValueError('Phone number must match pattern +1234567890')
        

def check_format_file(script_name: str) -> None:
    _, extension = os.path.splitext(script_name)
    if extension != '.py':
        raise ValueError('File to be Python-file')
    
    
def check_script_exist_in_db(script_name: str) -> None:
    db = get_db(DB_NAME)
    existing_script = db[COLLECTION_SCRIPT].find_one({'name': script_name})
    if existing_script:
        raise ValueError('Script name exists in db')
 

def check_docs_in_scripts_data(script_name: str) -> None:
    db = get_db(DB_NAME)
    collection = db[script_name]
    docs = collection.find()
    docs_list = list(docs)
    if not docs_list:
        raise ValueError('Docs must be not empty or your python script has misstakes')
    for doc in docs:
        check_doc = doc.get['name'] or doc.get['phone'] or doc.get['text_message'] or phone_must_match_pattern(doc.get['phone'])
        if not check_doc:   
            raise ValueError('Docs must have name, phone, text_message and phone must match pattern')
        if not doc.get(FIELD_SENT_SMS_ID):
            raise ValueError(f'In docs dont must be field {FIELD_SENT_SMS_ID}')

def check_validated_script(script_name: str) -> bool:
    try:
        check_format_file(script_name)
        check_script_exist_in_db(script_name)
        run_python_script(script_name)
        check_docs_in_scripts_data(script_name)
    except Exception as e:
        raise ValueError(e)
    finally:
        db = get_db(DB_NAME)
        collection = db[script_name]
        collection.drop()
    return True       
            