import csv
import urllib2
from sgrequests import SgRequests
import json

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
           'content-type': 'application/json',
           'X-Requested-With': 'XMLHttpRequest'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    url = 'https://www.escada.com/us/storelocator/'
    r = session.get(url, headers=headers)
    Found = False
    cty = '<MISSING>'
    state = '<MISSING>'
    cities = []
    for line in r.iter_lines():
        if 'city-select is--hidden" data-country="CA"' in line or 'city-select is--hidden" data-country="US"' in line:
            Found = True
            cty = line.split('data-country="')[1].split('"')[0]
            state = line.split('data-state="')[1].split('"')[0]
        if Found and '</select>' in line:
            Found = False
        if Found and '<option value="' in line and '<option value=""' not in line:
            city = line.split('<option value="')[1].split('"')[0]
            cities.append(cty + '|' + state + '|' + city)
    for city in cities:
        cty2 = city.split('|')[0]
        state2 = city.split('|')[1]
        loc = city.split('|')[2]
        payload = {"esc_store[country]":cty2,"esc_store[state]":state2,"esc_store[city]":loc}
        ajax_url = 'https://www.escada.com/us/storelocator/ajaxGetStores'
        r = session.post(ajax_url, headers=headers, data=json.dumps(payload))
        StoreFound = False
        for line in r.iter_lines():
            if 'window.storeLocator.stores.push' in line and StoreFound is False:
                StoreFound = True
                website = 'escada.com'
                name = line.split('"name1":"')[1].split('"')[0]
                add = line.split('"street":"')[1].split('"')[0]
                city = line.split('"city":"')[1].split('"')[0]
                state = line.split('"state":"')[1].split('"')[0]
                zc = line.split('"zipCode":"')[1].split('"')[0]
                phone = line.split('"phone":"')[1].split('"')[0]
                hours = '<MISSING>'
                if '"openingHours":' in line:
                    days = line.split('openingHours":[')[1].split(']')[0].split('"start":')
                    week = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
                    for day in days:
                        if '"end"' in day:
                            print(day)
                            hrs = day.split('"hours":"')[1].split('"')[0]
                            sday = week[int(day.split(',')[0])]
                            eday = week[int(day.split('"end":')[1].split(',')[0])]
                            if sday == eday:
                                text = sday + ': '
                            else:
                                text = sday + '-' + eday + ': '
                            if hours == '<MISSING>':
                                hours = text + hrs
                            else:
                                hours = hours + '; ' + text + hrs
                country = line.split('"countryIso":"')[1].split('"')[0]
                typ = 'Store'
                store = line.split('{"id":')[1].split(',')[0]
                lat = line.split('"lat":')[1].split(',')[0]
                lng = line.split('"lon":')[1].split(',')[0]
                yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
