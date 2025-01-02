# dht22aws

This project aims to have a set of devices (e,g, raspberrypi) with a DHT22 sensor attached and store it via API (POST request)
The DHT22 sensor gets the values from Temperature and Humidity in the physical environment.

Later on, it is possible to use a webpage with javascript to fetch those values from the storage and plotting into graph.
This can be useful to observe the physical enviroment energy efficiency and if we are having a healthy environment.

## Dependencies and prerequisites
- Acquire DHT22 sensor
- Acquire raspberrypi or Arduino
- Cloud environments such AWS to have storage and endpoints.

# Configuration

### Step 1
If first time with fresh checkout create virtual environment first by doing
```
sudo apt install python3 python3-pip python3-venv
python -m venv ./venv
```

Activating the virtual environment run
```
source venv/bin/activate
```

Installing the required dependencies aka libraries in the virtual environment
```
pip install -r requirements.txt
```

### Step 2
All basic configuration should be done in envrionment.py file
```
DEVICE_ID = "YOUR_ID" # Device Id in DB
DB_TABLE = "YOUR_TABLE" # Table name in remote storage
SLEEP = "YOUR_FREQUENCY" # frequency for each DHT22 reading 
API_URL = "ENDPOINT"  # Replace with your API Gateway URL
API_KEY = "KEY" # API key obtained from API Gateway
```

## Running it

Running the script to collect the data and send to storage
```
python3 dht22aws.py
```

## Logging

It is possible to monitoring these requests across dht22aws.log file

## Frontend

Simple index.html file can be found under "web" directory.
It fetches data from storage and displaying into a graph.
NOTE: the URL and API_KEY in the file requires adjustment.

