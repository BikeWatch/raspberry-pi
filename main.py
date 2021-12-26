import serial

supported_types = ["roll", "pitch", "lat", "long", "alt", "date", "time", "uuid"]

if __name__ == '__main__':
    ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1000)
    ser.flush()

    while True:
        dataset = {}
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
                        dataset[data_type] = value

                print(dataset)