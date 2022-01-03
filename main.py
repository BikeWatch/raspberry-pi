import serial
import requests

base_api_url = "https://bikewatch-functions.azurewebsites.net/api/"
active_uuid = ""
supported_types = ["roll", "pitch", "lat", "long", "alt", "date", "speed", "time", "uuid"]
dataset = []


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
                item = i.split(": ")
                data_type = item[0]
                value = item[1].replace(" |", "")
                if data_type in supported_types:
                    if data_type == "uuid":
                        set_uuid(value)
                    else:
                        data[data_type] = value
            if active_uuid != "":
                dataset.append(data)


def send_data_to_server():
    global dataset

    if active_uuid == "":
        return

    print(f'{base_api_url}StoreTelemetric')
    print({
         "uuid": active_uuid,
         "telemetric": dataset
    })
    # r = requests.post(
    #     f'{base_api_url}StoreTelemetric', {
    #     "uuid": active_uuid,
    #     "telemetric": dataset
    # })
    # print(r.status_code)
    # if r.status_code == 201:
    #     print("Data has been send to server")
    #     dataset = []
    # dataset = []


def loop():
    get_data_from_arduino()
    if len(dataset) >= 20:
        send_data_to_server()


if __name__ == '__main__':
    ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1000)
    ser.flush()

    while True:
        loop()