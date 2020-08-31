#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
import time
import serial
from threading import Timer
import sys
import os
from datetime import datetime
from influxdb import InfluxDBClient
import argparse

parser=argparse.ArgumentParser(
    description='''Script for Query SML Values from Electric Meter.''')
parser.add_argument('--device', type=str, required=False, default="/dev/ttyUSB0", help='Path to SML Reader Device.')
parser.add_argument('--influx_ip', type=str, required=True, default="", help='IP of the Influx DB Server.')
parser.add_argument('--influx_port', type=str, required=True, default="", help='Port of the Influx DB Server.')
parser.add_argument('--influx_user', type=str, required=True, default="", help='User of the Influx DB Server.')
parser.add_argument('--influx_pw', type=str, required=True, default="", help='Password of the Influx DB Server.')
parser.add_argument('--influx_db', type=str, required=True, default="", help='DB name of the Influx DB Server.')
parser.add_argument('--write', type=int, required=False, default=1, choices=[0, 1], help='Specify if Data should be written to InfluxDB or not.')
args=parser.parse_args()

mystring = b""
crc16_x25_table = [
    0x0000, 0x1189, 0x2312, 0x329B, 0x4624, 0x57AD,    0x6536, 0x74BF,
    0x8C48, 0x9DC1, 0xAF5A, 0xBED3, 0xCA6C, 0xDBE5, 0xE97E, 0xF8F7,
    0x1081, 0x0108,    0x3393, 0x221A, 0x56A5, 0x472C, 0x75B7, 0x643E,
    0x9CC9, 0x8D40, 0xBFDB, 0xAE52, 0xDAED, 0xCB64,    0xF9FF, 0xE876,
    0x2102, 0x308B, 0x0210, 0x1399,    0x6726, 0x76AF, 0x4434, 0x55BD,
    0xAD4A, 0xBCC3,    0x8E58, 0x9FD1, 0xEB6E, 0xFAE7, 0xC87C, 0xD9F5,
    0x3183, 0x200A, 0x1291, 0x0318, 0x77A7, 0x662E,    0x54B5, 0x453C,
    0xBDCB, 0xAC42, 0x9ED9, 0x8F50,    0xFBEF, 0xEA66, 0xD8FD, 0xC974,
    0x4204, 0x538D,    0x6116, 0x709F, 0x0420, 0x15A9, 0x2732, 0x36BB,
    0xCE4C, 0xDFC5, 0xED5E, 0xFCD7, 0x8868, 0x99E1,    0xAB7A, 0xBAF3,
    0x5285, 0x430C, 0x7197, 0x601E,    0x14A1, 0x0528, 0x37B3, 0x263A,
    0xDECD, 0xCF44,    0xFDDF, 0xEC56, 0x98E9, 0x8960, 0xBBFB, 0xAA72,
    0x6306, 0x728F, 0x4014, 0x519D, 0x2522, 0x34AB,    0x0630, 0x17B9,
    0xEF4E, 0xFEC7, 0xCC5C, 0xDDD5,    0xA96A, 0xB8E3, 0x8A78, 0x9BF1,
    0x7387, 0x620E,    0x5095, 0x411C, 0x35A3, 0x242A, 0x16B1, 0x0738,
    0xFFCF, 0xEE46, 0xDCDD, 0xCD54, 0xB9EB, 0xA862,    0x9AF9, 0x8B70,
    0x8408, 0x9581, 0xA71A, 0xB693,    0xC22C, 0xD3A5, 0xE13E, 0xF0B7,
    0x0840, 0x19C9,    0x2B52, 0x3ADB, 0x4E64, 0x5FED, 0x6D76, 0x7CFF,
    0x9489, 0x8500, 0xB79B, 0xA612, 0xD2AD, 0xC324,    0xF1BF, 0xE036,
    0x18C1, 0x0948, 0x3BD3, 0x2A5A,    0x5EE5, 0x4F6C, 0x7DF7, 0x6C7E,
    0xA50A, 0xB483,    0x8618, 0x9791, 0xE32E, 0xF2A7, 0xC03C, 0xD1B5,
    0x2942, 0x38CB, 0x0A50, 0x1BD9, 0x6F66, 0x7EEF,    0x4C74, 0x5DFD,
    0xB58B, 0xA402, 0x9699, 0x8710,    0xF3AF, 0xE226, 0xD0BD, 0xC134,
    0x39C3, 0x284A,    0x1AD1, 0x0B58, 0x7FE7, 0x6E6E, 0x5CF5, 0x4D7C,
    0xC60C, 0xD785, 0xE51E, 0xF497, 0x8028, 0x91A1,    0xA33A, 0xB2B3,
    0x4A44, 0x5BCD, 0x6956, 0x78DF,    0x0C60, 0x1DE9, 0x2F72, 0x3EFB,
    0xD68D, 0xC704,    0xF59F, 0xE416, 0x90A9, 0x8120, 0xB3BB, 0xA232,
    0x5AC5, 0x4B4C, 0x79D7, 0x685E, 0x1CE1, 0x0D68,    0x3FF3, 0x2E7A,
    0xE70E, 0xF687, 0xC41C, 0xD595,    0xA12A, 0xB0A3, 0x8238, 0x93B1,
    0x6B46, 0x7ACF,    0x4854, 0x59DD, 0x2D62, 0x3CEB, 0x0E70, 0x1FF9,
    0xF78F, 0xE606, 0xD49D, 0xC514, 0xB1AB, 0xA022,    0x92B9, 0x8330,
    0x7BC7, 0x6A4E, 0x58D5, 0x495C,    0x3DE3, 0x2C6A, 0x1EF1, 0x0F78]

class Watchdog_timer:
    def __init__(self, timeout, userHandler=None):
        self.timeout = timeout
        self.handler = userHandler if userHandler is not None else self.defaultHandler
        self.timer = Timer(self.timeout, self.handler)
        self.timer.start()
 
    def reset(self):
        self.timer.cancel()
        self.timer = Timer(self.timeout, self.handler)
        self.timer.start()
 
    def stop(self):
        self.timer.cancel()
 
    def defaultHandler(self):
        raise self

def crc16_x25(Buffer):
    crcsum = 0xffff
    global crc16_x25_table
    Buffer = [b'%c' % i for i in Buffer]
    for byte in Buffer:
        crcsum = crc16_x25_table[(ord(byte) ^ crcsum) & 0xff] ^ (crcsum >> 8 & 0xff)
    crcsum ^= 0xffff
    return crcsum

str_consumption = "77070100010800ff"
str_supply = "77070100020800ff"
str_actpower = "77070100100700ff"

def twos_comp(val, bits):
    if (val & (1 << (bits - 1))) != 0:
        val = val - (1 << bits)
    return val

def watchdogtimer_ovf():
    global mystring
    message = mystring[0:-2]
    crc_calc = crc16_x25(message)
    crc_rx = int(str(hex(mystring[-1]))[2:]+str(hex(mystring[-2]))[2:] ,16)
    if crc_rx == crc_calc:
        if message[0:8] == b'\x1b\x1b\x1b\x1b\x01\x01\x01\x01':
            message = mystring.hex()
            counter_consumption = "---"
            counter_supply = "---"
            counter_actpower = "---"
            if message.find(str_consumption):
                start_consumption = message.find(str_consumption)+(len(str_consumption))
                end_consumption = message[start_consumption:].find("0177")
                value_consumption = message[start_consumption:start_consumption+end_consumption+2]
                lengh_consumption_str = int(value_consumption[value_consumption.find("621e52ff")+(len("621e52ff")+1):value_consumption.find("621e52ff")+(len("621e52ff")+2)])-1
                counter_consumption = int(value_consumption[value_consumption.find("621e52ff")+(len("621e52ff")+2):value_consumption.find("621e52ff")+(len("621e52ff")+2)+lengh_consumption_str*2], 16)/10
            if message.find(str_supply):
                start_supply = message.find(str_supply)+(len(str_supply))
                end_supply = message[start_supply:].find("0177")
                value_supply = message[start_supply:start_supply+end_supply+2]
                lengh_supply_str = int(value_supply[value_supply.find("621e52ff")+(len("621e52ff")+1):value_supply.find("621e52ff")+(len("621e52ff")+2)])-1
                counter_supply = int(value_supply[value_supply.find("621e52ff")+(len("621e52ff")+2):value_supply.find("621e52ff")+(len("621e52ff")+2)+lengh_supply_str*2], 16)/10
            if message.find(str_actpower):
                start_actpower = message.find(str_actpower)+(len(str_actpower))
                end_actpower = message[start_actpower:].find("010101")
                value_actpower = message[start_actpower:start_actpower+end_actpower+2]
                lengh_actpower_str = int(value_actpower[value_actpower.find("621b5200")+(len("621b5200")+1):value_actpower.find("621b5200")+(len("621b5200")+2)])-1
                counter_actpower = twos_comp(int(value_actpower[value_actpower.find("621b5200")+(len("621b5200")+2):value_actpower.find("621b5200")+(len("621b5200")+2)+lengh_actpower_str*2], 16), lengh_actpower_str*8)
            print(datetime.now(), "Consumption: ", counter_consumption, "Wh, ", "Supply: ", counter_supply, "Wh, ", "Actual Power: ", counter_actpower, "W")
            if counter_consumption != "---" and counter_supply != "---" and args.write == 1:
                client = InfluxDBClient(host=args.influx_ip, port=args.influx_port, username=args.influx_user, password=args.influx_pw)
                client.switch_database(args.influx_db)
                json_body = [{
                    "measurement": "electric_meter",
                    "time": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
                    "fields": {
                        "consumption": int(counter_consumption),
                        'supply': int(counter_supply)
                    }
                }]
                #print(datetime.now(), "InfluxDB write data DEBUG:" + str(json_body))
                influx_result = client.write_points(json_body)
                if influx_result:
                    print(datetime.now(), "InfluxDB write data successfull:" + str(json_body))
                else:
                    print(datetime.now(), "InfluxDB write data FAILED:" + str(json_body))
                    print(influx_result)
                client.close()
                os._exit(0)
            watchdog.stop()
            mystring=b""
        else:
            mystring=b""
            watchdog.stop()
    else:
        mystring=b""
        watchdog.stop()

try:
    my_tty = serial.Serial(port=args.device, baudrate = 9600, parity =serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=0)
    sys.stdout.write(my_tty.portstr + " opened\n\n")
    my_tty.close()
    my_tty.open()
 
except Exception as e:
    sys.stdout.write("seriel port could not be opened:\n" + str(e) + "\n\n")
    exit()

try:
    my_tty.reset_input_buffer()
    my_tty.reset_output_buffer()
    watchdog = Watchdog_timer(0.1, watchdogtimer_ovf)
    watchdog.stop()
    while True:
        while my_tty.in_waiting > 0:
            mystring += my_tty.read()
            watchdog.reset()

except KeyboardInterrupt:
    my_tty.close()
    sys.stdout.write("\nscript manually exited!\n")
