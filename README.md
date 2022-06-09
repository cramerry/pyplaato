# Python API client for fetching Plaato data

  * Credits for this API client go to [JohNan/pyplaato](https://github.com/JohNan/pyplaato).

  * Client fetches data for the Plaato Keg (scale) using the official API, and publishes to Splunk HEC endpoint.

  * To be able to query the API an `auth_token` is required and which can be obtained by following [these](https://plaato.zendesk.com/hc/en-us/articles/360003234717-Auth-token) instructions

  * Create a tools/splunk.py file with Splunk HEC endpoint & headers, example:
    
    splunk_ep = https://[SplunkIP]:8088/services/collector/event
    
    headers2 = {'Authorization': 'Splunk [SplunkToken]', 'Content-Type': 'application/json'}

  * For more information about the available pins that can be retrieved please see the official [docs](https://plaato.zendesk.com/hc/en-us/articles/360003234877-Pins) from Plaato

## Usage
```
usage: cli.py -t AUTH_TOKEN -d keg

optional arguments:
  -h, --help            show this help message and exit

required arguments:
  -t AUTH_TOKEN         Auth token received from Plaato
  -d {keg,airlock}
```

### Disclaimer
This python library was not made by Plaato. It is not official, not developed, and not supported by Plaato.
