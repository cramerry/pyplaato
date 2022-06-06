import argparse
import asyncio
import sys
from datetime import datetime

import aiohttp
import requests
import urllib3
urllib3.disable_warnings()
import splunk

from pyplaato.plaato import (
    Plaato,
    PlaatoDeviceType
)

urllib3.disable_warnings()

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
        #print(f"Device type: {result.device_type}")
        #print(f"Name: {result.name}")
        #print(f"Firmware: {result.firmware_version}")
        print(f"Date: {datetime.fromtimestamp(result.date).strftime('%c')}")
        #print("Sensors:")
        print("Percent CO2 remaining: "f"{result.percent_beer_left}, " "lbs CO2 remaining: "f"{result.beer_left}")
        # add in result.
        #for key, attr in result.sensors.items():
        #    print(f"{result.get_sensor_name(key)}: {attr} {result.get_unit_of_measurement(key)}")
        data = {'index':'test', 'sourcetype':'json_no_timestamp', 'source':'co2', 'host':'rp4', 'event':{'perc_co2_left':result.percent_beer_left, 'lbs_co2_left':result.beer_left}}
        r = requests.post(splunk.splunk_ep, headers=splunk.headers2, json=data, verify=False)
        #r = requests.post(splunk_ep, headers=headers, json={'source':'plaato' 'sourcetype': 'Auto', 'host':'rp4', 'index':'test','fields':{'fieldname':fieldvalue}}, verify=False)        #RC
        #print("Binary Sensors:")
        #for key, attr in result.binary_sensors.items():
        #    print(f"\t{result.get_sensor_name(key)}: {attr}")
        #print("Attributes:")
        #for key, attr in result.attributes.items():
        #    print(f"\t{key}: {attr}")


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
