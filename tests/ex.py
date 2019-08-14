from pywavefleet.sofar import SofarApi, get_spotters
from pywavefleet.wavefleet import Spotter

# dat = get_devices()

# sptr1 = dat[0]
# sptr1.update()

api = SofarApi()
devs = api.get_devices()
_temp = devs[0]
sptr = Spotter(_temp['spotterId'], _temp['name'])
sptr.update()
print(sptr.latest_data())
print('d')