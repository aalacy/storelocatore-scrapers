import csv
from sgrequests import SgRequests
import json

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
           'content-type': 'application/json',
           'ModuleId': '2852',
           'TabId': '1135'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    locs = []
    url = 'https://www.rememberingalife.com/API/Nfda/Locator/locations/GetByBoundingBox'
    payload = {"pagination":{"pageSize":5000,"pageNumber":1},
               "sort":{"sortDirection":"ASC","fieldName":"Distance"},
               "filter":{},
               "LocationTopRight":{"latitude":65.0,
                                   "longitude":-60},
               "LocationCenter":{"latitude":44.30204501194119,
                                 "longitude":-90.75295410156251},
               "LocationBottomLeft":{"latitude":10.5,
                                     "longitude":-175.0},
               "distanceInMiles":5000}
    r = session.post(url, headers=headers, data=json.dumps(payload))
    for line in r.iter_lines():
        line = str(line.decode('utf-8'))
        if '{"LocationKey":"' in line:
            items = line.split('{"LocationKey":"')
            for item in items:
                if '"Name":"' in item:
                    name = item.split('"Name":"')[1].split('"')[0]
                    website = 'nfda.org'
                    lat = item.split('"Latitude":')[1].split(',')[0]
                    lng = item.split('"Longitude":')[1].split(',')[0]
                    country = item.split('"CountryIsoCode":"')[1].split('"')[0]
                    state = item.split('"RegionIsoCode":"')[1].split('"')[0]
                    city = item.split(',"City":"')[1].split('"')[0]
                    add = item.split('"StreetAddress1":"')[1].split('"')[0]
                    try:
                        add = add + ' ' + item.split('"StreetAddress2":"')[1].split('"')[0]
                    except:
                        pass
                    zc = item.split('"PostalCode":"')[1].split('"')[0]
                    phone = item.split('"telephone":"')[1].split('"')[0]
                    typ = '<MISSING>'
                    store = '<MISSING>'
                    hours = '<MISSING>'
                    loc = '<MISSING>'
                    if phone == '':
                        phone = '<MISSING>'
                    yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
    payload = {"pagination":{"pageSize":5000,"pageNumber":2},
               "sort":{"sortDirection":"ASC","fieldName":"Distance"},
               "filter":{},
               "LocationTopRight":{"latitude":65.0,
                                   "longitude":-60},
               "LocationCenter":{"latitude":44.30204501194119,
                                 "longitude":-90.75295410156251},
               "LocationBottomLeft":{"latitude":10.5,
                                     "longitude":-175.0},
               "distanceInMiles":5000}
    r = session.post(url, headers=headers, data=json.dumps(payload))
    for line in r.iter_lines():
        line = str(line.decode('utf-8'))
        if '{"LocationKey":"' in line:
            items = line.split('{"LocationKey":"')
            for item in items:
                if '"Name":"' in item:
                    name = item.split('"Name":"')[1].split('"')[0]
                    website = 'nfda.org'
                    lat = item.split('"Latitude":')[1].split(',')[0]
                    lng = item.split('"Longitude":')[1].split(',')[0]
                    country = item.split('"CountryIsoCode":"')[1].split('"')[0]
                    state = item.split('"RegionIsoCode":"')[1].split('"')[0]
                    city = item.split(',"City":"')[1].split('"')[0]
                    add = item.split('"StreetAddress1":"')[1].split('"')[0]
                    try:
                        add = add + ' ' + item.split('"StreetAddress2":"')[1].split('"')[0]
                    except:
                        pass
                    zc = item.split('"PostalCode":"')[1].split('"')[0]
                    phone = item.split('"telephone":"')[1].split('"')[0]
                    typ = '<MISSING>'
                    store = '<MISSING>'
                    hours = '<MISSING>'
                    loc = '<MISSING>'
                    if phone == '':
                        phone = '<MISSING>'
                    yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
    payload = {"pagination":{"pageSize":5000,"pageNumber":3},
               "sort":{"sortDirection":"ASC","fieldName":"Distance"},
               "filter":{},
               "LocationTopRight":{"latitude":65.0,
                                   "longitude":-60},
               "LocationCenter":{"latitude":44.30204501194119,
                                 "longitude":-90.75295410156251},
               "LocationBottomLeft":{"latitude":10.5,
                                     "longitude":-175.0},
               "distanceInMiles":5000}
    r = session.post(url, headers=headers, data=json.dumps(payload))
    for line in r.iter_lines():
        line = str(line.decode('utf-8'))
        if '{"LocationKey":"' in line:
            items = line.split('{"LocationKey":"')
            for item in items:
                if '"Name":"' in item:
                    name = item.split('"Name":"')[1].split('"')[0]
                    website = 'nfda.org'
                    lat = item.split('"Latitude":')[1].split(',')[0]
                    lng = item.split('"Longitude":')[1].split(',')[0]
                    country = item.split('"CountryIsoCode":"')[1].split('"')[0]
                    state = item.split('"RegionIsoCode":"')[1].split('"')[0]
                    city = item.split(',"City":"')[1].split('"')[0]
                    add = item.split('"StreetAddress1":"')[1].split('"')[0]
                    try:
                        add = add + ' ' + item.split('"StreetAddress2":"')[1].split('"')[0]
                    except:
                        pass
                    zc = item.split('"PostalCode":"')[1].split('"')[0]
                    phone = item.split('"telephone":"')[1].split('"')[0]
                    typ = '<MISSING>'
                    store = '<MISSING>'
                    hours = '<MISSING>'
                    loc = '<MISSING>'
                    if phone == '':
                        phone = '<MISSING>'
                    yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
