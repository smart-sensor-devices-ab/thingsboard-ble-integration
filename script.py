from bleuio_lib.bleuio_funcs import BleuIO
import time
import json
import requests

scan_data = []
def my_scan_callback(scan_input):
    global scan_data
    scan_data.append(scan_input)
    #print("\n\nmy_evt_callbacksss: " + str(scan_input))    
def convertNumber(data, start, end):
    pos = data.find("5B070")
    return int.from_bytes(
        bytes.fromhex(data[pos + start : pos + start + end])[::-1], byteorder="big"
    )
def adv_data_decode(data):
    pos = data.find("5B070")
    temp_hex = convertNumber(data, 22, 4)
    if temp_hex > 1000:
        temp_hex = (temp_hex - (65535 + 1)) / 10
    else:
        temp_hex = temp_hex / 10

    env_data = {
        "boardID": data[pos + 8 : pos + 8 + 6],
        "type": int(data[pos + 6 : pos + 6 + 2], 16),
        "light": convertNumber(data, 14, 4),
        "pressure": convertNumber(data, 18, 4) / 10,
        "temperature": temp_hex,
        "humidity": convertNumber(data, 26, 4) / 10,
        "voc": convertNumber(data, 30, 4),
        "co2": int(data[pos + 46 : pos + 46 + 4], 16),
    }

    return env_data
my_dongle = BleuIO()

my_dongle.register_scan_cb(my_scan_callback)
my_dongle.at_central()
my_dongle.at_findscandata('220069')
time.sleep(3)
my_dongle.stop_scan()
last_element = scan_data[-1]
data_part = json.loads(last_element[0])['data']
last_part = data_part.split(',')[-1].strip('"}')
decodedEnvData = adv_data_decode(last_part)
api_endpoint = 'https://thingsboard.cloud/api/v1/YOUR_API_KEY/telemetry'
response = requests.post(api_endpoint, json=decodedEnvData)
if response.status_code == 200:
    print("Data sent successfully to ThingsBoard.")
else:
    print("Failed to send data to ThingsBoard. Status code:", response.status_code)
print(decodedEnvData)


