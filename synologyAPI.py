####################
# IMPORTS

# Synology API
from synology_api import core_sys_info, surveillancestation
# Python API / JSON creator | #UNUSED
from flask import Flask, jsonify
# PPrint | #UNUSED
import pprint
# JSON creator | #USUSED
import json



####################
# MANUAL DATA

# Default JSON
default_data = {
    "camera_info": {
        "active": 0,
        "inactive": 0
        },
    "system_info": {
        "cpu_usage": "0%",
        "memory_usage": "0%",
        "available_storage": "0 TB",
        "ups_percentage": "N/A"
        }
    }

# Credentials
nasIp = '192.168.1.140'
nasPort = '5001'
username = 'username'
password = 'password'



####################
# SYNOLOGY API CALLS

# System Info API
apiCall_1 = core_sys_info.SysInfo(nasIp, nasPort, username, password, secure=True, cert_verify=False, dsm_version=7, debug=True, otp_code=None)
# SurveillanceStation API
apiCall_2 = surveillancestation.SurveillanceStation(nasIp, nasPort, username, password, secure=True, cert_verify=False, dsm_version=7, debug=True, otp_code=None)



####################
# DATA MANAGEMENT / ORGANIZATION

# Edit Default JSON function
def insert_data(default_data, active, inactive, cpu, memory, storage, ups):
    new_data = default_data
    
    new_data["camera_info"]["active"] = active
    new_data["camera_info"]["inactive"] = inactive
    new_data["system_info"]["cpu_usage"] = f"{cpu}%"
    new_data["system_info"]["memory_usage"] = f"{memory}%"
    new_data["system_info"]["available_storage"] = f"{storage} TB"
    if 0 <= ups <= 100:
        new_data["system_info"]["ups_percentage"] = f"{ups}%"

    return new_data

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

# Volume Availability Function
def volume_availability(storage_info):
    
    total_size = storage_info['data']['vol_info'][0]['total_size']
    used_size = storage_info['data']['vol_info'][0]['used_size']

    available_size = int(total_size) - int(used_size)
    available_size = available_size / (1024 ** 4)
    available_size = round(available_size, 2)
    
    return available_size

# UPS Activity Function  
#def ups_activity(ups_info):



####################
# API PULLS

# CPU Usage (%)
cpu_usage = (apiCall_1.get_cpu_utilization()['5min_load'])
# Memory Usage (%)
memory_usage = (apiCall_1.get_memory_utilization()['real_usage'])
# Active Camera Count
camera_active = (camera_activity(apiCall_2.camera_list())[0])
# Inactive Camera Count
camera_inactive = (camera_activity(apiCall_2.camera_list())[1])
# Available Storage (TB)
storage_available = (volume_availability(apiCall_1.get_volume_info()))
# UPS Power (%)
ups = 100



####################
# UPDATE JSON

# Print Updated JSON | #FOR TEST PURPOSES
print(insert_data(default_data, camera_active, camera_inactive, cpu_usage, memory_usage, storage_available, ups))






