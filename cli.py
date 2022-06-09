import argparse
import asyncio
import sys
from datetime import datetime
import aiohttp


from pyplaato.plaato import (
    Plaato,
    PlaatoDeviceType
)

# splunk-related dependencies
import requests
import urllib3
urllib3.disable_warnings()
import splunk

# mqtt-related dependencies
import paho.mqtt.client as mqtt
broker_url = "192.168.7.248"
broker_port = 1884


async def go(args):
    headers = {}
    if args.api_key:
        headers["x-api-key"] = args.api_key
    plaato = Plaato(args.auth_token, args.url, headers)

    async with aiohttp.ClientSession() as session:
        if args.device == 'keg':
            device_type = PlaatoDeviceType.Keg
        if args.device == 'airlock':
            device_type = PlaatoDeviceType.Airlock
        result = await plaato.get_data(session, device_type)
        print(f"Date: {datetime.fromtimestamp(result.date).strftime('%c')}")
        print("Percent CO2 remaining: "f"{result.percent_beer_left}, " "lbs CO2 remaining: "f"{result.beer_left}, " "LeakStatus: "f"{result.leak_detection}")

        # send data to Splunk HEC
        data = {'index':'test', 'sourcetype':'json_no_timestamp', 'source':'co2', 'host':'rp4', 'event':{'perc_co2_left':result.percent_beer_left, 'lbs_co2_left':result.beer_left, 'LeakDetected':result.leak_detection}}
        r = requests.post(splunk.splunk_ep, headers=splunk.headers2, json=data, verify=False)

        # send data to Edge Hub MQTT topics /beer/perc-co2-left
        client = mqtt.Client()
        client.connect(broker_url, broker_port)
        client.publish(topic="CO2R", payload=result.percent_beer_left, qos=1, retain=False)

def main():
    parser = argparse.ArgumentParser()
    required_argument = parser.add_argument_group('required arguments')
    optional_argument = parser.add_argument_group('optional arguments')
    required_argument.add_argument('-t', dest='auth_token',
                                   help='Auth token received from Plaato',
                                   required=True)
    required_argument.add_argument('-d',
                                   action='store',
                                   dest='device',
                                   choices=['keg', 'airlock'],
                                   required=True)
    optional_argument.add_argument('-u', dest='url',
                                   help='Mock url')
    optional_argument.add_argument('-k', dest='api_key',
                                   help='Header key for mock url')

    args = parser.parse_args()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(go(args))
    loop.close()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Aborting..')
        sys.exit(1)
