import csv
import urllib2
from sgrequests import SgRequests
import json
import ast

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
           'content-type': 'application/json'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    url = 'https://www.cvs.com/mcservices/minuteClinic/clinicLocator?version=1.0&serviceName=clinicLocator&operationName=getClinicLocationInfo&deviceType=DESKTOP&apiKey=a2ff75c6-2da7-4299-929d-d670d827ab4a&apiSecret=a8df2d6e-b11c-4b73-8bd3-71afc2515dae&serviceCORS=False&appName=MCL_WEB&deviceID=device12345&deviceToken=12232434&lineOfBusiness=MINUTE_CLINIC&channelName=WEB'
    states = []
    payload = {"request": {"state": "default"}}
    r = session.post(url, headers=headers, data=json.dumps(payload))
    locs = []
    array = json.loads(r.content)
    for item in array['response']['state']:
        states.append(item.split('(')[1].split(')')[0])
    for state in states:
        print('Pulling State %s...' % state)
        surl = 'https://www.cvs.com/mcservices/minuteClinic/clinicLocator?version=1.0&serviceName=clinicLocator&operationName=getClinicLocationInfo&deviceType=DESKTOP&apiKey=a2ff75c6-2da7-4299-929d-d670d827ab4a&apiSecret=a8df2d6e-b11c-4b73-8bd3-71afc2515dae&serviceCORS=False&appName=MCL_WEB&deviceID=device12345&deviceToken=12232434&lineOfBusiness=MINUTE_CLINIC&channelName=WEB'
        payload2 = {"request": {"state": state}}
        r2 = session.post(surl, headers=headers, data=json.dumps(payload2))
        array2 = json.loads(r2.content)
        for city in array2['response']['cityDetails']:
            for loc in city['clinicDetails']:
                locs.append(loc['clinicId'])

    for loc in locs:
        print('Pulling Location %s...' % loc)
        locstring = '["' + loc + '"]'
        lurl = 'https://www.cvs.com/mcservices/minuteClinic/getStoreDetails?operationName=getStoreDetails&serviceName=getStoreDetails&version=3.0&deviceType=DESKTOP&apiKey=a2ff75c6-2da7-4299-929d-d670d827ab4a&apiSecret=a8df2d6e-b11c-4b73-8bd3-71afc2515dae&serviceCORS=False&appName=MCL_WEB&deviceID=device12345&deviceToken=12232434&lineOfBusiness=MINUTE_CLINIC&channelName=WEB'
        payloads = '{"request": {"destination": {"minuteClinicID": ["' + loc + '"]},"operation": ["clinicInfo","waittime"],"services": ["indicatorMinuteClinicService"]}}'
        payload2 = ast.literal_eval(payloads)
        r2 = session.post(lurl, headers=headers, data=json.dumps(payload2))
        sarray = json.loads(r2.content)
        for item in sarray['response']['details']['locations']:
            store = item['StoreNumber']
            name = 'Minute Clinic #' + store
            website = 'minuteclinic.com'
            typ = item['minuteClinicName']
            add = item['addressLine']
            city = item['addressCityDescriptionText']
            state = item['addressState']
            zc = item['addressZipCode']
            lat = item['geographicLatitudePoint']
            lng = item['geographicLongitudePoint']
            try:
                phone = item['storePhonenumber']
            except:
                phone = '<MISSING>'
            country = 'US'
            hours = 'Mon: ' + item['minuteClinicHours']['DayHours'][0]['Hours']
            hours = hours + '; Tue: ' + item['minuteClinicHours']['DayHours'][1]['Hours']
            hours = hours + '; Wed: ' + item['minuteClinicHours']['DayHours'][2]['Hours']
            hours = hours + '; Thu: ' + item['minuteClinicHours']['DayHours'][3]['Hours']
            hours = hours + '; Fri: ' + item['minuteClinicHours']['DayHours'][4]['Hours']
            hours = hours + '; Sat: ' + item['minuteClinicHours']['DayHours'][5]['Hours']
            hours = hours + '; Sun: ' + item['minuteClinicHours']['DayHours'][6]['Hours']
            yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
