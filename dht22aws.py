import time
import board
import adafruit_dht
from decimal import Decimal
import datetime
import logging
from logging.handlers import RotatingFileHandler
import requests
import environment

logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
rootLogger = logging.getLogger()
rootLogger.setLevel(logging.INFO)

fileHandler = RotatingFileHandler("dht22aws.log", maxBytes=10000)
fileHandler.setFormatter(logFormatter)
rootLogger.addHandler(fileHandler)

# Initialize DHT22 sensor
#### dht_device = adafruit_dht.DHT22(board.D4) # data pin from DHT22 which is connected


def store_via_api(dt_string, temperature, humidity):
    apiUrl = environment.API_URL
    apiKey = environment.API_KEY
    headers = {
        'Content-Type': 'application/json',
        'X-Api-Key': apiKey
        }
    payload = {
            'timestamp': dt_string,
            'id': environment.DEVICE_ID,
            'temperature': temperature,
            'humidity': humidity
    }

    response = requests.post(apiUrl, json=payload, headers=headers)

    rootLogger.info("Status Code: {} Response Body: {}".format(response.status_code, response.json()))


def get_and_store():
    while True:
        try:
            temperature = 77 #Decimal(str(dht_device.temperature))
            humidity = 15 #Decimal(str(dht_device.humidity))

            # datetime object containing current date and time
            now = datetime.datetime.now(datetime.UTC)

            # Convert to ISO 8601 format string
            dt_string  = now.isoformat()

            rootLogger.info("Temp:{:.1f} C  Humidity: {}%".format(temperature, humidity))

            store_via_api(dt_string, temperature, humidity)

            time.sleep(int(environment.SLEEP))

        except RuntimeError as e:
            print(f"Error: {e}")


if __name__ == '__main__':
    try:
        get_and_store()
    except KeyboardInterrupt:
        print("Bye bye...")
