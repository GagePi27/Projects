####################
# IMPORTS

# Synology API (pip3 install git+https://github.com/N4S4/synology-api)  **must be from git repository for surveillancestation
from synology_api import core_sys_info, surveillancestation

# Python FastAPI (pip3 insatll fastapi)
from fastapi import FastAPI
from pydantic import BaseModel

# Time Alternative  (Python 3.7+)
import asyncio

# Copy (Python 1.5.2+)
from copy import deepcopy



####################
# MANUAL DATA

# Default JSON
default_data = {
    'system_info': {'cpu_usage': 'N/A', 'memory_usage': 'N/A', 'available_storage': 'N/A', 'ups_percentage': 'N/A'},
    'camera_info': {'active': 0, 'inactive': 0},
}

# Credentials
nasIp = '192.168.1.140'
nasPort = '5001'
username = 'remote_stats'
password = '9Z8mpRzW'



####################
# CLASSES

class SystemInfo(BaseModel):
    cpu_usage: str
    memory_usage: str
    available_storage: str
    ups_percentage: str

class CameraInfo(BaseModel):
    active: int
    inactive: int

class JsonData(BaseModel):
    system_info: SystemInfo
    camera_info: CameraInfo
    


####################
# DATA MANAGEMENT / ORGANIZATION

# Edit Default JSON function
def insert_data(ready_data, cpu, memory, storage, ups, active, inactive):
    new_data = ready_data
    
    new_data["camera_info"]["active"] = active
    new_data["camera_info"]["inactive"] = inactive
    new_data["system_info"]["cpu_usage"] = f"{cpu}%"
    new_data["system_info"]["memory_usage"] = f"{memory}%"
    new_data["system_info"]["available_storage"] = f"{storage} TB"
    if 0 <= ups <= 100:
        new_data["system_info"]["ups_percentage"] = f"{ups}%"

    return new_data
    
# Volume Availability Function
def volume_availability(storage_info):
    
    total_size = storage_info['data']['vol_info'][0]['total_size']
    used_size = storage_info['data']['vol_info'][0]['used_size']

    available_size = round((int(total_size) - int(used_size)) / (1024 ** 4), 2)
    
    return available_size

# UPS Activity Function  
#def ups_activity(ups_info):

# Camera Activity Function
def camera_activity(camera_info):
    active = 0
    inactive = 0
    
    if 'cameras' in camera_info.get('data', {}):
        for camera in camera_info['data']['cameras']:
            # Check the camera's 'status' key
            if camera.get('status') == 1:
                active += 1
            else:
                inactive += 1

    return [active, inactive]



####################
# START API

app = FastAPI()



####################
# DATA COLLECTION

# Auto Update API Data
async def call_pull_update_data():
    while True:
        
        # Copy Default Data
        ready_data = deepcopy(default_data)

        # Globalize updated_data for API
        global updated_data

        #Try / Except (Stops Synology API from breaking from a loss of connection)
        try:
            # Synology API Calls
            apiCall_1 = core_sys_info.SysInfo(nasIp, nasPort, username, password, secure=True, cert_verify=False, dsm_version=7, debug=True, otp_code=None)
            apiCall_2 = surveillancestation.SurveillanceStation(nasIp, nasPort, username, password, secure=True, cert_verify=False, dsm_version=7, debug=True, otp_code=None)

            # Synology API Pulls
            cpu_usage = str(int(apiCall_1.get_cpu_utilization()['system_load']) + int(apiCall_1.get_cpu_utilization()['user_load']))
            memory_usage = apiCall_1.get_memory_utilization()['real_usage']
            storage_available = volume_availability(apiCall_1.get_volume_info())
            ups = 100  # NEED TO MAKE UPS STUFF
            camera_active = camera_activity(apiCall_2.camera_list())[0]
            camera_inactive = camera_activity(apiCall_2.camera_list())[1]

            # Update Data
            updated_data = insert_data(ready_data, cpu_usage, memory_usage, storage_available, ups, camera_active, camera_inactive)

        except:
            updated_data = ready_data

        # API Wait
        await asyncio.sleep(5) # Wait time (in seconds) between API data updates



####################
# UPDATE API

# Startup Tasks
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(call_pull_update_data())

# API Tasks
@app.get("/data", response_model=JsonData)
async def update_api():
    # Convert updated_data into a Pydantic Model
    api_data = JsonData(**updated_data)
    return api_data
