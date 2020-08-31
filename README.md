# electrical-meter
Script to read SML messages from electrical meter and save it to InfluxDB.

Electric meters offer e.g. total power consumption counter via SML (Smart Message Language) IR interface. See [SML](https://de.wikipedia.org/wiki/Smart_Message_Language) and [OBIS Numbers](https://de.wikipedia.org/wiki/OBIS-Kennzahlen) Wikipedia articles. The messages can be captured by an simply IR reader with USB connection (search for "smartmeter Optokopf").

Based on the work and Python script [SML-Interface script](http://www.stefan-weigert.de/php_loader/sml.php) attached script will read the messages in configureable intervals (default 300s) and save the counter values to InfluxDB.


## Part List
USB IR Reader <50€


## Create a Docker Container

```bash
mkdir electric-meter
cd electric-meter/
curl -O https://raw.githubusercontent.com/Froschie/electrical-meter/master/Dockerfile
curl -O https://raw.githubusercontent.com/Froschie/electrical-meter/master/get_electric_meter.py
curl -O https://raw.githubusercontent.com/Froschie/electrical-meter/master/get_electric_meter_start.py
docker build --tag electrical-meter .
```

## Run Script manually (no writing to InfluxDB)

```bash
docker exec -it --rm -e influx_ip=192.168.1.3 -e influx_port=8086 -e influx_user=user -e influx_pw=pw --device=/dev/ttyUSB0 electrical-meter
/get_electric_meter.py --influx_ip=$influx_ip --influx_port=$influx_port --influx_user=$influx_user --influx_pw=$influx_pw --influx_db=$influx_db --device=$device --write=0
```

Example Output:
```
/dev/ttyUSB0 opened

2020-08-31 15:32:39.667895 Consumption:  100000.1 Wh,  Supply:  100000.7 Wh,  Actual Power:  -800 W
2020-08-31 15:32:40.662338 Consumption:  100000.1 Wh,  Supply:  100000.9 Wh,  Actual Power:  -800 W
2020-08-31 15:32:41.666824 Consumption:  100000.2 Wh,  Supply:  100000.9 Wh,  Actual Power:  125 W
^C
script manually exited!
```
Negative Values mean generated power from photovoltaik is suplied to the grid. Positive values mean power is taken from grid.


## Start a Docker Container via CMD Line
```
docker run -d --name electrical-meter --restart unless-stopped -e influx_ip=192.168.1.3 -e influx_port=8086 -e influx_user=user -e influx_pw=pw -e interval=300 --device=/dev/ttyUSB0 electrical-meter
```

## Start a Docker Container via Docker-Compose File
```yaml
version: '3'

services:
  <influxdb-service-name>:
    image: influxdb:latest
    container_name: <influxdb_container_name>
    ports:
      - 8086:8086
    volumes:
      - </some_folder>:/var/lib/influxdb
    environment:
      - INFLUXDB_HTTP_AUTH_ENABLED=true
      - INFLUXDB_MONITOR_STORE_ENABLED=false
      - INFLUXDB_DB=<db>
      - INFLUXDB_ADMIN_USER=<admin>
      - INFLUXDB_ADMIN_PASSWORD=<pw1>
      - INFLUXDB_USER=<user>
      - INFLUXDB_USER_PASSWORD=<pw2>
      - INFLUXDB_READ_USER=<read>
      - INFLUXDB_READ_USER_PASSWORD=<pw3>
    restart: unless-stopped
  electric-meter-query:
    image: electric-meter
    container_name: electric-meter-query
    environment:
      - influx_ip=192.168.1.3
      - influx_port=8086
      - influx_user=<user>
      - influx_pw=<pw2>
      - influx_db=<db>
      - interval=300
    devices:
      - /dev/ttyUSB0
    restart: unless-stopped
```
Please adapt the parameters in <> brackets, use external folder to save the database and use matching values in the python script configuration!
