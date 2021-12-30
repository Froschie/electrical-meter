# electrical-meter ![Docker Hub image](https://github.com/Froschie/electrical-meter/workflows/Docker%20Hub%20image/badge.svg)

Script to read SML messages from electrical meter and save it to InfluxDB.  

Electric meters offer various informations via SML (Smart Message Language) IR interface.  
The [SML](https://de.wikipedia.org/wiki/Smart_Message_Language) protocol is using specified [OBIS Numbers](https://de.wikipedia.org/wiki/OBIS-Kennzahlen) which contain informations like actual power consumption or total energy usage.  
The messages can be captured by a simply IR reader with USB connection (search for "smartmeter Optokopf").  

My script is capturing all the SML messages and by using Python [smllib](https://github.com/spacemanspiff2007/SmlLib) Library decoding it.

The script was tested on a ISKRA MT631 electric meter with extended informations enabled (PIN from power operator necessary).

*Note: the smart meters (at least in Germany) are by default not providing detailed informations! This needs to be manually enabled. To do this please request the necessary PIN from your Energy Network Provider and then set the Energy Meter accordingly. Without extended informations enabled current power consumption is not transmitted and counters only provide Wh values with last 3x digits set to 0 (virtually reporting kWh only).*


## Part List
USB IR Reader <50€


## Start Docker Container  

Pull latest Image:  
`docker pull froschie/sml-electrical-meter:latest`  

Start Container to only query values:  
```
docker run -it --name temp --rm \
 --device /dev/ttyUSB0 \
 -e device="/dev/ttyUSB0" \
 -e TZ=Europe/Berlin \
 -e write="0" \
 -e interval=1 \
 -e influx_ip="" \
 froschie/sml-electrical-meter
```
*Note: please adapt the parameters as needed especially the device parameters!*  

Example Output:
```
2021-12-30 13:19:05.00203    INFO:      Actual Time: 2021-12-30 13:19:05.203273 waiting for: 2021-12-30 13:19:06
2021-12-30 13:19:07.00144    INFO:      96.50.1: ISK 96.1.0: 1234567890 1.8.0: 1234567.1Wh 2.8.0: 123456.1Wh 16.7.0: -50W
2021-12-30 13:19:08.00150    INFO:      96.50.1: ISK 96.1.0: 1234567890 1.8.0: 1234567.2Wh 2.8.0: 123456.2Wh 16.7.0: -25W
2021-12-30 13:19:09.00141    INFO:      96.50.1: ISK 96.1.0: 1234567890 1.8.0: 1234567.3Wh 2.8.0: 123456.3Wh 16.7.0: 0W
2021-12-30 13:19:10.00149    INFO:      96.50.1: ISK 96.1.0: 1234567890 1.8.0: 1234567.4Wh 2.8.0: 123456.4Wh 16.7.0: 25W
2021-12-30 13:19:11.00141    INFO:      96.50.1: ISK 96.1.0: 1234567890 1.8.0: 1234567.5Wh 2.8.0: 123456.5Wh 16.7.0: 50W
```

Negative Values mean generated power from photovoltaik is suplied to the grid. Positive values mean power is taken from grid.


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
curl -O https://raw.githubusercontent.com/Froschie/electrical-meter/master/query_electric_meter.py
curl -O https://raw.githubusercontent.com/Froschie/electrical-meter/master/influx_fields.json
curl -O https://raw.githubusercontent.com/Froschie/electrical-meter/master/obis_code_list.json
curl -O https://raw.githubusercontent.com/Froschie/electrical-meter/master/obis_unit_list.json
docker build --tag electrical-meter .
```

## Run Script without Docker (query only)

With latest Python Version execute:

```bash
pip install influxdb pyserial smllib
python query_electric_meter.py --device=/dev/ttyUSB0 --interval=1
```

To execute Test it in a Python Docker container: 

```bash
git clone https://github.com/Froschie/electrical-meter.git
cd electrical-meter
docker run -it --name temp --rm --device /dev/ttyUSB0 -v $(pwd):/mnt/em python bash
pip install influxdb pyserial smllib
cd /mnt/em
python query_electric_meter.py --device=/dev/ttyUSB0 --interval=1
```

## Script Options

| Option | Description |
| --- | --- |
| device | USB Device path, default: `/dev/ttyUSB0` |
| interval | Interval displaying the SML message, default `60`, any integer from "1" is allowed |
| obis | OBIS Code Format, default `SHORT` (e.g. 1.8.0), possible values: "SHORT", "LONG"(1-0.1.8.0), "NAME" (Positive active energy) |
| write | Enable writing to InluxDB usefull for debugging or initial testing, default `0` (Disabled), possible values: "0", "1" (enabled) |
| influx_ip | InfluxDB IP |
| influx_port | InfluxDB Port |
| influx_user | InfluxDB Username |
| influx_pw | InfluxDB Password |
| influx_db | Influx DB Name |
| unit | Unit Value Format when writing to InfluxDB, default: `INT` (Integer), possible values: "INT", "FLOAT" |
| log | Output Level, default: `INFO`, possible values: "DEBUG", "INFO", "WARNING", "ERROR" |

## Configuration files

The script uses 3x config files which can be modified if needed. The current files are based on the fields my Energy Meter is offering.

This file defines which fields are written to InfluxDB, `influx_fields.json`:
```json
{
    "tags": {
        "96.50.1": "device",
        "96.1.0": "serial"
    },
    "fields": {
        "1.8.0": "consumption",
        "2.8.0": "supply"
    }
}
```

This file defines the names for the OBIS codes, `obis_code_list.json`:
```json
{
    "96.50.1": "Manufacturer",
    "1.8.0": "Positive active energy",
    "2.8.0": "Negative active energy",
    "96.1.0": "Serial Number",
    "16.7.0": "Sum active instantaneous power"
}
```

This file defines the units of the OBIS values, `obis_unit_list.json`:
```json
{
    "30": "Wh",
    "27": "W"
}
```
