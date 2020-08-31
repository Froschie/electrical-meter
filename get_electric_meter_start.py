#!/usr/bin/env python3
import os
import subprocess
from datetime import datetime, timedelta
import time
influx_ip = os.environ['influx_ip']
influx_port = os.environ['influx_port']
influx_user = os.environ['influx_user']
influx_pw = os.environ['influx_pw']
influx_db = os.environ['influx_db']
device = os.environ['device']
write = os.environ['write']
interval = float(os.environ['interval'])

cmd = '/get_electric_meter.py --influx_ip="%s" --influx_port="%s" --influx_user="%s" --influx_pw="%s" --influx_db="%s" --device="%s" --write="%s"' % (influx_ip, influx_port, influx_user, influx_pw, influx_db, device, write)

# Time Rounding Function
def ceil_time(ct, delta):
    return ct + (datetime.min - ct) % delta

now = datetime.now()
new_time = ceil_time(now, timedelta(seconds=int(interval)))
print(now, "Actual Time:", now, "waiting for:", new_time)    

# Wait for Full Minute / Half Minute
while now < new_time:
    time.sleep(0.5)
    now = datetime.now()

try:
    while True:
        print(datetime.now(), "Query Electric Meter Values...")
        p = subprocess.Popen(cmd, shell=True)
        p.wait()
        p.terminate()
        time.sleep(interval - ((time.time() - new_time.timestamp()) % interval))
except KeyboardInterrupt:
    print("Script aborted...")
finally:
    print("Script exited...")
