# electrical-meter
Script to read SML messages from electrical meter and save it to InfluxDB.

Electric meters offer e.g. total power consumption counter via SML (Smart Message Language) IR interface. See [SML](https://de.wikipedia.org/wiki/Smart_Message_Language) and [OBIS Numbers](https://de.wikipedia.org/wiki/OBIS-Kennzahlen) Wikipedia articles. The messages can be captured by an simply IR reader with USB connection (search for "smartmeter Optokopf").

Based on the work and Python script [SML-Interface script](http://www.stefan-weigert.de/php_loader/sml.php) attached script will read the messages in configureable intervals (default 300s) and save the counter values to InfluxDB.


## Part List
USB IR Reader <50€


## Create a Docker Container

```bash
mkdir xxx
cd xxx/
curl -O https://raw.githubusercontent.com/Froschie/electrical-meter/master/Dockerfile
curl -O https://raw.githubusercontent.com/Froschie/electrical-meter/master/xxx.sh
curl -O https://raw.githubusercontent.com/Froschie/electrical-meter/master/xxx.py
docker build --tag electrical-meter .
```


## Docker Compose
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
```
Please adapt the parameters in <> brackets, use external folder to save the database and use matching values in the python script configuration!
