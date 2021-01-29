# electrical-meter ![Docker Hub image](https://github.com/Froschie/electrical-meter/workflows/Docker%20Hub%20image/badge.svg)

Script to read SML messages from electrical meter and save it to InfluxDB.  

Electric meters offer e.g. total power consumption counter via SML (Smart Message Language) IR interface. See [SML](https://de.wikipedia.org/wiki/Smart_Message_Language) and [OBIS Numbers](https://de.wikipedia.org/wiki/OBIS-Kennzahlen) Wikipedia articles. The messages can be captured by an simply IR reader with USB connection (search for "smartmeter Optokopf").

Based on the work and Python script [SML-Interface script](http://www.stefan-weigert.de/php_loader/sml.php) attached script will read the messages in configureable intervals (default 300s) and save the counter values to InfluxDB.

The script was tested on a ISKRA MT631 electric meter with extended informations enabled (PIN from power operator necessary).
Without extended informations enabled current power consumption is not transmitted and counters only provide Wh values with last 3x digits set to 0 (virtually reporting kWh only).


## Part List
USB IR Reader <50€


## Start Docker Container  

Pull latest Image:  
`docker pull froschie/sml-electrical-meter:latest`  

Start Container to only query values:  
```
docker run -it --rm \
 --device /dev/ttyUSB0 \
 -e TZ=Europe/Berlin \
 -e device="/dev/ttyUSB0" \
 -e write="0" \
 -e interval=1 \
 froschie/sml-electrical-meter
```
*Note: please adapt the parameters as needed!*  


## Start Docker Container via Docker-Compose  
```bash
curl -O https://raw.githubusercontent.com/Froschie/electrical-meter/master/docker-compose.yaml
vi docker-compose.yaml
docker-compose up -d
```
*Note: please adapt the parameters as needed!*


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
```bash
docker run -d --name electrical-meter --restart unless-stopped -e influx_ip=192.168.1.3 -e influx_port=8086 -e influx_user=user -e influx_pw=pw -e interval=300 --device=/dev/ttyUSB0 electrical-meter
```

## Start a Docker Container via Docker-Compose File
```bash
curl -O https://raw.githubusercontent.com/Froschie/electrical-meter/master/docker-compose.yaml
vi docker-compose.yaml
docker-compose up -d
```
*Note: please adapt the parameters in docker compose file as needed! Use external folder to save the database and use matching values in the python script configuration!*
