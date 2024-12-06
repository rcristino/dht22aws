import time
import board
import adafruit_dht
import boto3
from datetime import datetime
from decimal import Decimal
import logging
from logging.handlers import RotatingFileHandler
import environment

logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
rootLogger = logging.getLogger()
rootLogger.setLevel(logging.INFO)

fileHandler = RotatingFileHandler("dht22aws.log", maxBytes=10000)
fileHandler.setFormatter(logFormatter)
rootLogger.addHandler(fileHandler)

# Initialize DHT22 sensor
dht_device = adafruit_dht.DHT22(board.D4) # data pin from DHT22 which is connected

dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')
table = dynamodb.Table(environment.DB_TABLE)

def store_in_dynamodb(dt_string, temperature, humidity):
    table.put_item(
        Item={
            'timestamp': dt_string,
            'id': environment.DEVICE_ID,
            'temperature': temperature,
            'humidity': humidity
        }
    )


def get_and_store():
    while True:
        try:
            temperature = Decimal(str(dht_device.temperature))
            humidity = Decimal(str(dht_device.humidity))

            # datetime object containing current date and time
            now = datetime.utcnow()
            dt_string = now.strftime("%d-%m-%Y %H:%M:%S")

            store_in_dynamodb(dt_string, temperature, humidity)

            rootLogger.info("Temp:{:.1f} C  Humidity: {}%".format(temperature, humidity))

            time.sleep(int(environment.SLEEP))

        except RuntimeError as e:
            print(f"Error: {e}")


if __name__ == '__main__':
    try:
        get_and_store()
    except KeyboardInterrupt:
        print("Bye bye...")
