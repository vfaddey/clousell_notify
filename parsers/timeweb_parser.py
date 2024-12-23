import json
import time
from threading import Thread

import requests
from config import TIMEWEB_API_KEY, CLOUDSELL_API_TOKEN


config_list_url = 'https://api.timeweb.cloud/api/v1/presets/servers'
timeweb_provider_id = 'fddae35e-2e40-4771-a893-d60f07216fc8'

result = requests.get(config_list_url, headers={'Authorization': f'Bearer {TIMEWEB_API_KEY}'})

presets = result.json().get('server_presets', [])


def timer(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        res = func(*args, **kwargs)
        print(time.time() - start_time)
        return res
    return wrapper


@timer
def req(data):
    res = requests.post('http://31.129.54.116:8888/servers/',
                           data=json.dumps(data),
                           headers={'Authorization': f'Bearer {CLOUDSELL_API_TOKEN}'})
    print(res.json())


for preset in presets:
    server = {
        'name': preset.get('description_short', ''),
        'description': preset.get('description', ''),
        'price': preset.get('price', 0),
        'server_type': 'virtual',
        'provider_id': timeweb_provider_id,
        'billing_cycle': 'monthly',
        'features': {
            'processor_name': '',
            'ram_type': 'DDR4',
            'cores': preset.get('cpu', 0),
            'ram': preset.get('ram', 0),
            'disk_type': preset.get('disk_type', 0).upper(),
            'disk': preset.get('disk', 0),
            'core_frequency': preset.get('cpu_frequency', 0),
            'network_limit': preset.get('network_limit', 0),
            'location': preset.get('location', ''),
            'network_speed': preset.get('bandwidth', 0),
        },
        'additional_info': {
            'external_id': preset.get('id', ''),
        }
    }
    Thread(target=req, args=(server, )).start()
