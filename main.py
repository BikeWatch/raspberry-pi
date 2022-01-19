import serial
import requests
import ast
import json

ser = serial.Serial()
base_api_url = "https://bikewatch-functions.azurewebsites.net/api/"
active_uuid = ""
supported_types = ["roll", "pitch", "lat", "long", "alt", "date", "speed", "time", "uuid"]
dataset = []


def rework_types(val):
    try:
        val = ast.literal_eval(val)
    except:
        val = str(val)
    return val


def set_uuid(uuid):
    global active_uuid
    if active_uuid != uuid:
        print("uuid changed")
        active_uuid = uuid.replace(" ", "-")


def get_data_from_arduino():
    data = {}
    if ser.in_waiting > 0:
        line = ser.readline().decode('utf-8').rstrip()
        if "Info" in line:
            print(line)
        else:
            for i in line.split(' | '):
                try:
                    item = i.split(": ")
                    data_type = item[0]
                    value = item[1].replace(" |", "")
                    if data_type in supported_types:
                        if data_type == "uuid":
                            set_uuid(value)
                        else:
                            data[data_type] = rework_types(value)
                except IndexError as err:
                    print(err)
            if active_uuid != "":
                dataset.append(data)


def send_data_to_server():
    global dataset

    if active_uuid == "":
        return

    body = json.dumps({
        "uuid": active_uuid,
        "telemetric": dataset
    })
    print(body)
    r = requests.post(
        f'{base_api_url}StoreTelemetric', body)
    print(r.status_code)
    if r.status_code == 201:
        print("Data has been send to server")
        dataset = []


def loop():
    if ser is not None:
        get_data_from_arduino()
        if len(dataset) >= 20:
            send_data_to_server()


def initialize_serial():
    global ser
    try:
        ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1000)
        ser.flush()
    except:
        print("Failed to initialize serial connection to arduino")
        input("Press enter to continue")
        initialize_serial()


if __name__ == '__main__':
    initialize_serial()
    while True:
        loop()
