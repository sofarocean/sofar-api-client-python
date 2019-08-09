import sys; print('Python %s on %s' % (sys.version, sys.platform))
sys.path.extend(['/Users/mikesosa/Documents/Sofar/wavefleet-client-python'])
import json
import requests
from pywavefleet.api import SofarApi

s = SofarApi()
u1 = f"{s.endpoint}/history"


dat = {
  "spotterId": "asdsad",
  "startDate": "2017-01-29T12:00:42+00:00",
  "endDate": "2017-11-01T00:00:42+00:00"
}

hdr = {'token': s.token, 'Content-Type': 'application/json'}

queue = requests.post(u1, json=dat, headers=hdr)

if (queue.status_code == 200):
    js = json.loads(queue.text)
    print(js)
    file_id = js['data']['fileId']

    print(js)
    u2 = f"{s.endpoint}/datafile/{file_id}"
    status = json.loads(requests.get(u2, headers=hdr).text)
    print(status)
