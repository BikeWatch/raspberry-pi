import serial
import requests

base_api_url = ""
active_uuid = ""
supported_types = ["roll", "pitch", "lat", "long", "alt", "date", "speed", "time", "uuid"]
dataset = []


def set_uuid(uuid):
    global active_uuid
    if active_uuid is not uuid:
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
                        set_uuid(data[data_type])
                    else:
                        data[data_type] = value
            dataset.append(data)


def send_data_to_server():
    global dataset
    print({
        "uuid": active_uuid,
        "telemetric": dataset
    })
    r = requests.post(base_api_url + "/StoreTelemetric", {
        "uuid": active_uuid,
        "telemetric": dataset
    })
    if r.status_code == 201:
        print("Data has been send to server")
        dataset = []


def loop():
    get_data_from_arduino()
    if len(dataset) >= 20:
        send_data_to_server()


if __name__ == '__main__':
    ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1000)
    ser.flush()

    while True:
        loop()