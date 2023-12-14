# This module return response fake query in api sms
from faker import Faker

fake = Faker()


class FakeResponse:
    def __init__(self, status_code, content=None):
        self.status_code = status_code
        self.content = content
        
    def json(self):
        return self.content if self.content is not None else {}

def send_sms(url: str, data: dict) -> FakeResponse:
    exists_need_data = (data.get('name') and
                        data.get('text') and 
                        data.get('phone') and 
                        url)
    if  exists_need_data: 
        return FakeResponse(status_code=201, content={'id': fake.pystr()})
    return FakeResponse(status_code=400)
