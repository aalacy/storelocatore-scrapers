import csv
import os
from sgrequests import SgRequests
import datetime
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('starbucks_co_uk')



weekday = datetime.datetime.today().weekday()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)



session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }

def fetch_data():
    ids = []
    for x in range(1600, 1761):
        for y in range(17, -82, -1):
            xlat = float(float(x) / 30)
            ylng = float(float(y) / 10)
            logger.info(str(xlat) + ', ' + str(ylng))
            url = 'https://www.starbucks.co.uk/api/v1/store-finder?latLng=' + str(xlat) + '%2C' + str(ylng)
            r = session.get(url, headers=headers)
            array = json.loads(r.content)
            for item in array['stores']:
                website = 'starbucks.co.uk'
                store = item['storeNumber']
                name = item['name']
                try:
                    phone = item['phoneNumber']
                except:
                    phone = '<MISSING>'
                lat = item['coordinates']['lat']
                lng = item['coordinates']['lng']
                add = item['address'].split('\n')[0]
                cz = item['address'].split('\n')[1]
                if cz.count(' ') == 1:
                    zc = cz.split(' ')[0]
                    city = cz.split(' ')[1]
                if cz.count(' ') == 2:
                    zc = cz.split(' ')[0] + ' ' + cz.split(' ')[1]
                    city = cz.split(' ')[2]
                if cz.count(' ') == 3:
                    zc = cz.split(' ')[0] + ' ' + cz.split(' ')[1]
                    city = cz.split(' ')[2] + ' ' + cz.split(' ')[3]
                state = '<MISSING>'
                country = 'GB'
                typ = '<MISSING>'
                hours = ''
                weekdays = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
                today = weekdays[weekday]
                tom = weekdays[(weekday + 1) % 7]
                try:
                    hours = item['hoursNext7Days'][0]['name'] + ': ' + item['hoursNext7Days'][0]['description']
                    hours = hours + '; ' + item['hoursNext7Days'][1]['name'] + ': ' + item['hoursNext7Days'][1]['description']
                    hours = hours + '; ' + item['hoursNext7Days'][2]['name'] + ': ' + item['hoursNext7Days'][2]['description']
                    hours = hours + '; ' + item['hoursNext7Days'][3]['name'] + ': ' + item['hoursNext7Days'][3]['description']
                    hours = hours + '; ' + item['hoursNext7Days'][4]['name'] + ': ' + item['hoursNext7Days'][4]['description']
                    hours = hours + '; ' + item['hoursNext7Days'][5]['name'] + ': ' + item['hoursNext7Days'][5]['description']
                    hours = hours + '; ' + item['hoursNext7Days'][6]['name'] + ': ' + item['hoursNext7Days'][6]['description']
                    hours = hours.replace('Today',today).replace('Tomorrow',tom)
                except:
                    pass
                if country == 'GB':
                    if store not in ids:
                        ids.append(store)
                        if phone is None or phone == '':
                            phone = '<MISSING>'
                        if hours is None or hours == '':
                            hours = '<MISSING>'
                        if zc is None or zc == '':
                            zc = '<MISSING>'
                        purl = '<MISSING>'
                        yield [website, purl, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
