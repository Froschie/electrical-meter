# electrical-meter
Script to read SML messages from electrical meter and save it to InfluxDB.

Electric meters offer e.g. total power consumption counter via SML (Smart Message Language) IR interface. See [SML](https://de.wikipedia.org/wiki/Smart_Message_Language) and [OBIS Numbers](https://de.wikipedia.org/wiki/OBIS-Kennzahlen) Wikipedia articles. The messages can be captured by an simply IR reader with USB connection (search for "smartmeter Optokopf").

Based on the work and Python script [SML-Interface script](http://www.stefan-weigert.de/php_loader/sml.php) attached script will read the messages in configureable intervals (default 300s) and save the counter values to InfluxDB.
