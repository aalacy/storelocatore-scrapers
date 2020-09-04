import csv
import urllib.request, urllib.error, urllib.parse
import requests
import json
import datetime
from sgrequests import SgRequests
import sgzip

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }

search = sgzip.ClosestNSearch()
search.initialize(country_codes = ['us', 'ca'])

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "operating_info", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    ids = []
    coord = search.next_coord()
    locations = []
    while coord:
        x = str(coord[0])
        y = str(coord[1])
        num = 0
        url = 'https://www.olivegarden.com/web-api/restaurants'
        payload = {'geoCode': x + ',' + y,
                   'resultsPerPage': '10',
                   'resultsOffset': '0',
                   'displayDistance': 'true',
                   'locale': 'en_US'
                   }
        r = session.post(url, headers=headers, data=payload)
        if r.encoding is None: r.encoding = 'utf-8'
        website = 'olivegarden.com'
        result_coords = []
        for line in r.iter_lines(decode_unicode=True):
            if '"country":"' in line:
                items = line.split('"country":"')
                for item in items:
                    if '"corpNumber":"' in item:
                        num = num + 1
                        opinfo = '<MISSING>'
                        country = item.split('"')[0]
                        city = item.split('"city":"')[1].split('"')[0]
                        lat = item.split('"latitude":"')[1].split('"')[0]
                        store = item.split('"restaurantId":"')[1].split('"')[0]
                        if '"message":"' in item:
                            opinfo = item.split('"message":"')[1].split('"')[0]
                        lng = item.split('"longitude":"')[1].split('"')[0]
                        result_coords.append((lat, lng))
                        zc = item.split('"zip":"')[1].split('"')[0]
                        typ = 'Restaurant'
                        name = item.split('"restaurantName":"')[1].split('"')[0]
                        add = item.split('"AddressOne":"')[1].split('"')[0]
                        add = add + ' ' + item.split('"AddressTwo":"')[1].split('"')[0]
                        add = add.strip()
                        state = item.split('"state":"')[1].split('"')[0]
                        phone = item.split('"phoneNumber":"')[1].split('"')[0]
                        days = item.split('hourTypeDesc":"Hours of Operations"')
                        hours = '<MISSING>'
                        try:
                            hours = 'Mon: ' + days[1].split('startTime":"')[1].split('"')[0] + '-' + days[1].split('endTime":"')[1].split('"')[0]
                            hours = hours + '; Tue: ' + days[2].split('startTime":"')[1].split('"')[0] + '-' + days[1].split('endTime":"')[1].split('"')[0]
                            hours = hours + '; Wed: ' + days[3].split('startTime":"')[1].split('"')[0] + '-' + days[1].split('endTime":"')[1].split('"')[0]
                            hours = hours + '; Thu: ' + days[4].split('startTime":"')[1].split('"')[0] + '-' + days[1].split('endTime":"')[1].split('"')[0]
                            hours = hours + '; Fri: ' + days[5].split('startTime":"')[1].split('"')[0] + '-' + days[1].split('endTime":"')[1].split('"')[0]
                            hours = hours + '; Sat: ' + days[6].split('startTime":"')[1].split('"')[0] + '-' + days[1].split('endTime":"')[1].split('"')[0]
                            hours = hours + '; Sun: ' + days[7].split('startTime":"')[1].split('"')[0] + '-' + days[1].split('endTime":"')[1].split('"')[0]
                        except:
                            hours = '<MISSING>'
                        if store not in ids:
                            ids.append(store)
                            if phone is None or phone == '':
                                phone = '<MISSING>'
                            if hours is None or hours == '':
                                hours = '<MISSING>'
                            if zc is None or zc == '':
                                zc = '<MISSING>'
                            if country == 'GUAM':
                                country = 'US'
                                state = 'GU'
                            locations.append([website, '<MISSING>', name, opinfo, add, city, state, zc, country, store, phone, typ, lat, lng, hours])
        if len(result_coords) > 0:
            search.max_count_update(result_coords)
        else:
            search.max_distance_update(30.0)
        coord = search.next_coord()
    for loc in locations:
        yield loc


def scrape():
    data = fetch_data()
    write_output(data)

scrape()
