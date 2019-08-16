# Sofar Ocean API Python Client
Python Client for the Sofar Ocean Spotter API

### Requirements
- Python3 (Preferably 3.7) and pip
- python-dotenv
- requests
- Pytest (If developing/Contributing)
- Setuptools (If developing/Contributing)

### Installation
1. Make sure that you have the requirements listed above
2. `pip install pysofar` to your desired python environment
3. Create a file in your home directory (on unix `~/`) called `sofar_api.env`.
    Put your API token and key inside in the format `WF_API_TOKEN=<token>` 
    We have included an example file named [ex.sofar_api.env](ex.sofar_api.env) in the
    repository which you can copy (Just make sure to change the name and update the token
    to match yours). If you do not currently have an API token, log into your sofar account 
    [here](https://spotter.sofarocean.com). Open the sidebar and click `api`. You should 
    see a section called `Authentication` which will have a button to generate a token. 
    You can also use this to update your token to a new one, should you desire.
3. Test with `python3 -c 'import pysofar''`. If this runs successfully, chances are everything worked.
4. If you wish to develop/contribute to this project see [contributing](contributing.md).

### Basic Classes
Included here are basic descriptions of some of the classes. Further documentation is provided
within each function itself.

## Sofar.py
1. SofarApi: Initialize to get access most of the api endpoints
- Properties:
    - Devices (Spotters that belong to this account). List of Dictionaries of Id and Name
    - Device Ids. List of the id's of the devices
- Methods
    - get_device_location_data: Most recent location data of the devices
    - get_latest_data: Use to grab the latest data from a specific spotter
    - update_spotter_name: Update the name of a specific spotter
    - get_wave_data: Gets all of the wave data for all of the spotters in a date range
    - get_wind_data: Same as above but for wind
    - get_frequency_data: Same as above but for frequency
    - get_track_data: Same as above but for tracking data
    - get_all_data: Returns all of wave, wind, frequency, track for all spotters in a date range
    - get_spotters: Returns Spotter objects updated with data values
    
2. WaveDataQuery: Use for more fine tuned querying for a specific spotter
- Methods:
    - execute: Runs the query with the set parameters
    - limit: Limit of how many results to return
    - waves: Input True to include wave data in results
    - wind: ^ but for winds
    - track: ^ but for track
    - frequency: ^ but for frequency
    - directional_moments: Input true to include directional moments if frequency data is also included
    - set_start_date: Set the start date of the data to be queried
    - clear_start_date: No lower bound on the dates for the spotter data requested 
    - set_end_date: Sets the end date of data to be queried
    - clear_end_date: No upper bound on the dates for the spotter data requested

3. Miscellaneous Functions
- get_and_update_spotters: Same as SofarApi.get_spotters but can be used standalone

## Spotter.py
1. Spotter: Class representing a spotter and its properties
- Properties:
    - id
    - name
    - mode
    - lat
    - lon
    - battery_power
    - battery_voltage
    - solar_voltage
    - humidity
    - timestamp

- Methods:
    - change_name: Updates the spotters name
    - update: Updates the spotters attributes with the latest data values
    - latest_data: Gets latest_data from this spotter
    - grab_data: More fine tuned data querying for this spotter
    
    
### A small example
```python
from pysofar.sofar import SofarApi
from pysofar.spotter import Spotter

# init the api
api = SofarApi()
# get the devices belonging to you
devices = api.devices
print(devices)

# grab spotter objects for the devices
spotter_grid = api.get_spotters()
# each array value is a spotter object
spt_0 = spotter_grid[0]
print(spt_0.mode)
print(spt_0.lat)
print(spt_0.lon)
print(spt_0.timestamp)

# Get most recent data from the above spotter with waves
spt_0_dat = spt_0.latest_data()
print(spt_0_dat)

# what if we want frequency data with directional moments as well
spt_0_dat_freq = spt_0.latest_data(include_directional_moments=True)
print(spt_0_dat_freq)

# What about a specific range of time with waves and track data
spt_0_query = spt_0.grab_data(
    limit=100,
    start_date='2019-01-01',
    end_date='2019-06-30',
    include_track=True
)
print(spt_0_query)

# What if we want all data from all spotters over all time
# this will take a few seconds
all_dat = api.get_all_data()
print(all_dat.keys())
print(all_dat)
```


