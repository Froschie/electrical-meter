# pip install influxdb pyserial smllib
import serial
from smllib import SmlStreamReader
import logging
import sys
import os
import json
import time
from datetime import datetime, timedelta
from influxdb import InfluxDBClient
import argparse

parser=argparse.ArgumentParser(
    description='''Script for Query SML Values from Electric Meter.''')
parser.add_argument('--device', type=str, required=False, default="/dev/ttyUSB0", help='Path to SML Reader Device.')
parser.add_argument('--influx_ip', type=str, required=False, default="", help='IP of the Influx DB Server.')
parser.add_argument('--influx_port', type=str, required=False, default="", help='Port of the Influx DB Server.')
parser.add_argument('--influx_user', type=str, required=False, default="", help='User of the Influx DB Server.')
parser.add_argument('--influx_pw', type=str, required=False, default="", help='Password of the Influx DB Server.')
parser.add_argument('--influx_db', type=str, required=False, default="", help='DB name of the Influx DB Server.')
parser.add_argument('--write', type=int, required=False, default=0, choices=[0, 1], help='Specify if Data should be written to InfluxDB or not.')
parser.add_argument('--interval', type=int, required=False, default=60, help='Query interval in "s".')
parser.add_argument('--unit', type=str, required=False, default="INT", choices=["INT", "FLOAT"], help='Specify the used value format for InfluxDB.')
parser.add_argument('--obis', type=str, required=False, default="SHORT", choices=["SHORT", "LONG", "NAME"], help='Specify in which format the OBIS Codes should be displayed.')
parser.add_argument('--log', type=str, required=False, default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"], help='Specify Log output.')
args=parser.parse_args()

# Log Output configuration
logging.basicConfig(level=getattr(logging, args.log), format='%(asctime)s.%(msecs)05d %(levelname)07s:\t%(message)s', datefmt='%Y-%m-%d %H:%M:%S')
log = logging.getLogger(__name__)

# Time Rounding Function
def ceil_time(ct, delta):
    return ct + (datetime.min - ct) % delta

starttime = datetime.now()
now = datetime.now()
new_time = ceil_time(now, timedelta(seconds=int(args.interval)))
log.info("Actual Time: " + str(now) + " waiting for: " + str(new_time))

# Wait for Full Minute / Half Minute
while now < new_time:
    time.sleep(0.5)
    now = datetime.now()

my_tty = serial.Serial(port=args.device, baudrate=9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=0)
my_tty.close()
my_tty.open()
start = '1b1b1b1b01010101'
end = '1b1b1b1b1a'
data = ''

# Load OBIS Code List
try:
    for filename in ["obis_code_list.json", "/obis_code_list.json"]:
        if os.path.isfile(filename):
            with open(filename) as json_data_file:
                obis_code_list = json.load(json_data_file)
                break
except Exception as e:
    log.error("obis_code_list.json file could not be opened or is not valid JSON file!")
    log.error(e)
    time.sleep(60)
    sys.exit(1)

# Load OBIS Unit List
try:
    for filename in ["obis_unit_list.json", "/obis_unit_list.json"]:
        if os.path.isfile(filename):
            with open(filename) as json_data_file:
                obis_unit_list = json.load(json_data_file)
                break
except Exception as e:
    log.error("obis_unit_list.json file could not be opened or is not valid JSON file!")
    log.error(e)
    time.sleep(60)
    sys.exit(1)

# Load Influx Definiton for Tags and Fields
try:
    for filename in ["influx_fields.json", "/influx_fields.json"]:
        if os.path.isfile(filename):
            with open(filename) as json_data_file:
                influx_fields = json.load(json_data_file)
                break
except Exception as e:
    log.error("influx_fields.json file could not be opened or is not valid JSON file!")
    log.error(e)
    time.sleep(60)
    sys.exit(1)

def obis_code(value, format):
    obis_A = int(value[0:2], 16)
    obis_B = int(value[2:4], 16)
    obis_C = int(value[4:6], 16)
    obis_D = int(value[6:8], 16)
    obis_E = int(value[8:10], 16)
    if format == "SHORT" or format == "NAME":
        obis_string = "{}.{}.{}".format(obis_C, obis_D, obis_E)
    if format == "NAME" and obis_string in obis_code_list:
        obis_string = obis_code_list[obis_string]
    if format == "LONG":
        obis_string = "{}-{}:{}.{}.{}".format(obis_A, obis_B, obis_C, obis_D, obis_E)
    return obis_string

def obis_unit(unit):
    if str(unit) in obis_unit_list:
        return obis_unit_list[str(unit)]
    else:
        return ""

def obis_value(value, code):
    if code == "96.1.0":
        return str(int(value[-10:], 16)).rjust(10, '0')
    else:
        return str(value)

try:
    if args.influx_ip and args.influx_port and args.influx_user and args.influx_pw and args.influx_db:
        client = InfluxDBClient(host=args.influx_ip, port=args.influx_port, username=args.influx_user, password=args.influx_pw)
        client.switch_database(args.influx_db)
    while True:
        try:
            char = my_tty.read()
            data = data + char.hex()
            pos = data.find(end)
            if (pos != -1):
                for x in range(0, 3):
                    char = my_tty.read()
                    data = data + char.hex() 
                log.debug(data)
                stream = SmlStreamReader()
                stream.add(bytes.fromhex(data))
                sml_frame = stream.get_frame()
                if sml_frame is None:
                    continue
                obis_values = sml_frame.get_obis()
                text = ""
                if args.influx_ip and args.influx_port and args.influx_user and args.influx_pw and args.influx_db:
                    temp_body = {
                        "measurement": "electric_meter",
                        "tags": {},
                        "time": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
                        "fields": {}
                    }
                for item in obis_values:
                    code_short = obis_code(item.obis, "SHORT")
                    value = obis_value(item.get_value(), code_short)
                    if args.influx_ip and args.influx_port and args.influx_user and args.influx_pw and args.influx_db:
                        if code_short in influx_fields['tags']:
                            temp_body['tags'][influx_fields['tags'][code_short]] = value
                        if code_short in influx_fields['fields']:
                            points = client.query("SELECT last({}) FROM electric_meter WHERE serial='{}'".format(influx_fields['fields'][code_short], temp_body['tags']['serial'])).get_points()
                            last_value = 0
                            for point in points:
                                last_value = point['last']
                            if float(value) >= float(last_value) or points is None:
                                if args.unit == "INT":
                                    temp_body['fields'][influx_fields['fields'][code_short]] = int(float(value))
                                else:
                                    temp_body['fields'][influx_fields['fields'][code_short]] = float(value)
                            else:
                                log.warning("Point value below last recoded one! ({}: {})".format(influx_fields['fields'][code_short], value))
                    text += obis_code(item.obis, args.obis) + ": " + value + obis_unit(item.unit) + " "
                log.info(text)
                if args.influx_ip and args.influx_port and args.influx_user and args.influx_pw and args.influx_db:
                    try:
                        log.debug(temp_body)
                        json_body = [temp_body]
                        if args.write == 1:
                            influx_result = client.write_points(json_body)
                            if influx_result:
                                log.debug("InfluxDB write data successfull:" + str(json_body))
                            else:
                                log.error("InfluxDB write data FAILED:" + str(json_body))
                                log.error(influx_result)
                        #client.close()
                    except Exception as e:
                        log.error("InfluxDB writing failed: {}".format(e))
                time.sleep(args.interval - ((time.time() - new_time.timestamp()) % args.interval))
                data = ''
        except KeyboardInterrupt:
            log.warning("Script aborted...")
            break
        except Exception as e:
            log.debug("Something went wrong: {}".format(e))
            continue
except KeyboardInterrupt:
    log.warning("Script aborted...")
finally:
    log.info("Script ending...")
