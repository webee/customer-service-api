import json
from app import dbs


@dbs.transactional
def create_or_update_meta_data(proj, data):
    proj.meta_data = [proj.create_meta_data_item(item.get('key'),
                                                 json.dumps(item.get('type'), ensure_ascii=False),
                                                 json.dumps(item.get('value'), ensure_ascii=False),
                                                 item.get('label'),
                                                 item.get('index')) for item in data]
    dbs.session.add(proj)
