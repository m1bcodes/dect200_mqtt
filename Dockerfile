FROM python:latest
WORKDIR /usr/local/app

# Install the application dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy in the source code
COPY dect200_mqtt.py ./

# Setup an app user so the container doesn't run as the root user
RUN useradd app
USER app

#CMD ["python", "dect200_mqtt.py", "--fritzuser=fritz1050", "--fritzpw=9334", "--mqttbroker=192.168.178.48", "--interval=30", "--verbose"]
CMD python dect200_mqtt.py --fritzuser=$FRITZUSER --fritzpw=$FRITZPW --mqttbroker=$MQTT_BROKER --interval=$INTERVAL --verbose
# CMD tail -f /dev/null

