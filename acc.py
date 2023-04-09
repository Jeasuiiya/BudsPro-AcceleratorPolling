# python acc.py 0C:8D:CA:51:E4:F3

import os
import time
from datetime import datetime

import bluetooth
import argparse
import io

class AcceleratorSensorManager:
    def __init__(self, sock, data_cb, verbose=False, trace=False):
        self.sock = sock
        self.data_cb = data_cb
        self.verbose = verbose
        self.trace = trace
        self.buffer = io.BufferedWriter(io.FileIO("accelerator_data.txt", "wb"))

    def attach(self):
        self.sock.send(b'1')
        if self.verbose:
            print("Attached to device.")

    def detach(self):
        self.sock.send(b'0')
        if self.verbose:
            print("Detached from device.")
        self.buffer.close()

    def loop(self):
        while True:
            left = []
            right = []

            for i in range(3):
                left.append(int.from_bytes(self.sock.recv(2), byteorder='big', signed=True) / 16384.0)
            for i in range(3):
                right.append(int.from_bytes(self.sock.recv(2), byteorder='big', signed=True) / 16384.0)

            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
            self.buffer.write(f"x={left[0]}, y={left[1]}, z={left[2]}; x2={right[0]}, y2={right[1]}, z2={right[2]}, time={timestamp}\n".encode())
            self.data_cb(left, right, timestamp)
            time.sleep(0.01)

def __accelerator_sensor_callback(left, right, timestamp):
    # Each parameter is a float list containing the raw xyz values of the accelerometer
    # The values are ordered like this: x, y, z
    print(f"x={left[0]}, y={left[1]}, z={left[2]}; x2={right[0]}, y2={right[1]}, z2={right[2]}, time={timestamp}")

def main():
    parser = argparse.ArgumentParser(description="Accelerator Sensor Data")
    parser.add_argument("mac", help="Bluetooth MAC Address")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose Output")
    parser.add_argument("--trace", "-t", action="store_true", help="Trace Output")
    args = parser.parse_args()

    host = args.mac
    port = 1

    sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    sock.connect((host, port))

    if args.verbose:
        print("Connected to device.")

    sensor = None
    try:
        sensor = AcceleratorSensorManager(sock, __accelerator_sensor_callback, args.verbose, args.trace)
        sensor.attach()
        sensor.loop()
    except KeyboardInterrupt:
        if sensor is not None:
            sensor.detach()

if __name__ == '__main__':
    main()
