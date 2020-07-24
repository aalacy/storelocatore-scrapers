import csv
from sgrequests import SgRequests
import json

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
        url = 'https://www.pizzahut.ca/mobilem8-web-service/rest/storeinfo/distance?_=1579704724574&latitude=43.6802493&longitude=-79.32094169999999&maxResults=2500&radius=5000&statuses=ACTIVE&statuses=TEMP-INACTIVE&tenant=ph-canada'
        r = session.get(url, headers=headers, timeout=60)
        for line in r.iter_lines():
            line = str(line.decode('utf-8'))
            if '{"storeId":' in line:
                items = line.split('{"storeId":')
                for item in items:
                    if '"tenantId":"' in item:
                        website = 'pizzahut.ca'
                        hours = ''
                        store = item.split(',')[0]
                        name = "Pizza Hut"
                        add = item.split('"street":"')[1].split('"')[0]
                        city = item.split('"city":"')[1].split('"')[0]
                        state = item.split('"state":"')[1].split('"')[0]
                        country = 'CA'
                        zc = item.split('"zipCode":"')[1].split('"')[0]
                        lat = item.split('"latitude":')[1].split(',')[0]
                        lng = item.split('"longitude":')[1].split(',')[0]
                        typ = '<MISSING>'
                        purl = '<MISSING>'
                        try:
                            phone = item.split('"phoneNumber":"')[1].split('"')[0]
                        except:
                            phone = '<MISSING>'
                        days = item.split(',{"openTime":')
                        for day in days:
                            if '"franchiseNm":"' not in day:
                                try:
                                    hrs = day.split('"timeString":"')[1].split(',')[1].split('"')[0].strip().split(' ')[0] + '; ' + day.split('"timeString":"')[1].split(',')[0] + '-' + day.split('"timeString":"')[2].split(',')[0]
                                    if hours == '':
                                        hours = hrs
                                    else:
                                        hours = hours + '; ' + hrs
                                except:
                                    pass
                        if hours == '':
                            hours = '<MISSING>'
                        yield [website, purl, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
