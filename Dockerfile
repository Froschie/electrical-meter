# first build Alpine Base Image with Init
FROM alpine:3.12
RUN apk add --no-cache bash tzdata

# Image Description
LABEL version="4.0" description="Script to read Electric Meter via SML."

# Install Python and Python Modules
RUN apk add --no-cache python3 py-pip && pip install influxdb pyserial smllib && apk del py-pip && apk add py3-requests py3-msgpack

# Define Environment Variables needed for Script
ENV device="/dev/ttyUSB0" influx_ip="192.168.1.3" influx_port="8086" influx_user="user" influx_pw="pw" influx_db="measurements" device="/dev/ttyUSB0" write="1" interval="300" unit="INT" obis="SHORT" log="INFO"

# Copy Scriptis to Container
ADD ./influx_fields.json /influx_fields.json
ADD ./obis_code_list.json /obis_code_list.json
ADD ./obis_unit_list.json /obis_unit_list.json
ADD ./query_electric_meter.py /query_electric_meter.py
ENTRYPOINT /usr/bin/python3 -u /query_electric_meter.py --device=$device --influx_ip=$influx_ip --influx_port=$influx_port --influx_user=$influx_user --influx_pw=$influx_pw --influx_db=$influx_db --device=$device --write=$write --interval=$interval --unit=$unit --obis=$obis --log=$log
