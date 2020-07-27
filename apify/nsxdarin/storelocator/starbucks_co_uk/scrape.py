import csv
import os
from sgrequests import SgRequests
import datetime
import json

weekday = datetime.datetime.today().weekday()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)



session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
           'accept': 'application/json',
           'x-requested-with': 'XMLHttpRequest'
           }

def fetch_data():
    ids = []
    for x in range(1494, 1761):
        for y in range(17, -82, -1):
            xlat = float(float(x) / 30)
            ylng = float(float(y) / 10)
            print(str(xlat) + ', ' + str(ylng))
            url = 'https://www.starbucks.co.uk/bff/locations?lat=' + str(xlat) + '&lng=' + str(ylng)
            r = session.get(url, headers=headers)
            try:
                array = json.loads(r.content)
                for item in array['stores']:
                    website = 'starbucks.co.uk'
                    store = item['storeNumber']
                    name = item['name']
                    phone = item['phoneNumber']
                    lat = item['coordinates']['latitude']
                    lng = item['coordinates']['longitude']
                    add = item['address']['streetAddressLine1']
                    try:
                        add = add + ' ' + item['address']['streetAddressLine2']
                    except:
                        pass
                    try:
                        add = add + ' ' + item['address']['streetAddressLine3']
                    except:
                        pass
                    add = add.strip()
                    city = item['address']['city']
                    state = item['address']['countrySubdivisionCode']
                    country = item['address']['countryCode']
                    zc = item['address']['postalCode']
                    typ = item['brandName']
                    hours = ''
                    weekdays = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
                    today = weekdays[weekday]
                    tom = weekdays[(weekday + 1) % 7]
                    try:
                        hours = item['schedule'][0]['dayName'] + ': ' + item['schedule'][0]['hours']
                        hours = hours + '; ' + item['schedule'][1]['dayName'] + ': ' + item['schedule'][1]['hours']
                        hours = hours + '; ' + item['schedule'][2]['dayName'] + ': ' + item['schedule'][2]['hours']
                        hours = hours + '; ' + item['schedule'][3]['dayName'] + ': ' + item['schedule'][3]['hours']
                        hours = hours + '; ' + item['schedule'][4]['dayName'] + ': ' + item['schedule'][4]['hours']
                        hours = hours + '; ' + item['schedule'][5]['dayName'] + ': ' + item['schedule'][5]['hours']
                        hours = hours + '; ' + item['schedule'][6]['dayName'] + ': ' + item['schedule'][6]['hours']
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
            except:
                pass

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
