FROM python:slim

# Image Description
LABEL version="2.0" description="Script to read Electric Meter via SML"

# Install required Python Modules
RUN pip install influxdb pyserial

# Set correct Timezone
RUN ln -sf /usr/share/zoneinfo/Europe/Berlin /etc/localtime

# Define Environment Variables needed for Script
ENV influx_ip="192.168.1.3" influx_port="8086" influx_user="user" influx_pw="pw" influx_db="measurements" device="/dev/ttyUSB0" write="1" interval="300"

# Install pgrep for stopping the Python Script in case needed
RUN apt-get update && apt-get install -y procps htop dos2unix

# Copy Scriptis to Container
ADD ./get_electric_meter.py /get_electric_meter.py
ADD ./get_electric_meter_start.py /get_electric_meter_start.py
RUN chmod +x /get_electric_meter.py /get_electric_meter_start.py
RUN dos2unix /get_electric_meter.py && dos2unix /get_electric_meter_start.py

# Default Command for starting the Container
CMD ["/get_electric_meter_start.py"]