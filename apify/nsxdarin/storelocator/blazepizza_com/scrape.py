import csv
from sgrequests import SgRequests
import json
from sgzip import sgzip

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
           'locale': 'en_US'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    ids = []
    for coord in sgzip.coords_for_radius(50):
        try:
            x = coord[0]
            y = coord[1]
            url = 'https://nomnom-prod-api.blazepizza.com/restaurants/near?lat=' + str(x) + '&long=' + str(y) + '&radius=500&limit=20&nomnom=calendars&nomnom_calendars_from=20201020&nomnom_calendars_to=20201028&nomnom_exclude_extref=999'
            #print('Pulling Lat-Long %s,%s...' % (str(x), str(y)))
            r = session.get(url, headers=headers)
            for line in r.iter_lines():
                line = str(line.decode('utf-8'))
                if '"id":' in line:
                    items = line.split('"id":')
                    for item in items:
                        if '"isavailable":' in item:
                            hours = ''
                            store = item.split(',')[0]
                            lat = item.split('"latitude":')[1].split(',')[0]
                            lng = item.split('"longitude":')[1].split(',')[0]
                            loc = item.split('"mobileurl":"')[1].split('"')[0]
                            name = item.split(',"name":"')[1].split('"')[0]
                            state = item.split('"state":"')[1].split('"')[0]
                            add = item.split(',"streetaddress":"')[1].split('"')[0]
                            phone = item.split('"telephone":"')[1].split('"')[0]
                            zc = item.split('"zip":"')[1].split('"')[0]
                            city = item.split('"city":"')[1].split('"')[0]
                            typ = '<MISSING>'
                            website = 'blazepizza.com'
                            country = item.split(',"country":"')[1].split('"')[0]
                            days = item.split('"label":null,"ranges":[')[1].split(']')[0].split('"end":"')
                            for day in days:
                                if '"start":"' in day:
                                    hrs = day.split('"weekday":"')[1].split('"')[0] + ': ' + day.split('"start":"')[1].split('"')[0].rsplit(' ',1)[1] + '-' + day.split('"')[0].rsplit(' ',1)[1]
                                    if hours == '':
                                        hours = hrs
                                    else:
                                        hours = hours + '; ' + hrs
                            if phone ==  '':
                                phone = '<MISSING>'
                            if hours ==  '':
                                hours = '<MISSING>'
                            if store not in ids:
                                ids.append(store)
                                yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
        except:
            pass

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
