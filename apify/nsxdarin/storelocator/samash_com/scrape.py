import csv
import urllib2
import requests
import json

session = requests.Session()
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
    url = 'https://hosted.where2getit.com/samashmusic/rest/getlist?lang=en_US'
    payload = {"request":{"appkey":"F1BBEE32-0D3E-11DF-AB7B-8CB43B999D57","formdata":{"objectname":"Account::State","where":{"country":"US"}}}}
    r = session.post(url, data=json.dumps(payload), headers=headers)
    states = []
    for line in r.iter_lines():
        if ',"name":"' in line:
            items = line.split(',"name":"')
            for item in items:
                if '"altname":"' in item:
                    states.append(item.split('"')[0])
    for state in states:
        print('Pulling State %s...' % state)
        url = 'https://hosted.where2getit.com/samashmusic/rest/getlist?lang=en_US'
        payload = {"request":{"appkey":"F1BBEE32-0D3E-11DF-AB7B-8CB43B999D57","formdata":{"order":"city","-softmatch":"1","objectname":"Locator::Store","where":{"clientkey":{"eq":""},"state":{"eq":state},"name":{"ilike":""}}}}}
        r = session.post(url, data=json.dumps(payload), headers=headers)
        for line in r.iter_lines():
            if '"local_page_photobanner":"' in line:
                items = line.split('"local_page_photobanner":"')
                for item in items:
                    if 'local_page_photoimage' in item:
                        website = 'samash.com'
                        name = item.split('"name":"')[1].split('"')[0].strip()
                        add = item.split('"address1":"')[1].split('"')[0]
                        city = item.split('"city":"')[1].split('"')[0]
                        state = item.split(',"state":"')[1].split('"')[0]
                        zc = item.split('"postalcode":"')[1].split('"')[0]
                        phone = item.split('"phone":"')[1].split('"')[0]
                        hours = 'Mon-Thu: ' + item.split('"hoursmonthur":"')[1].split('"')[0]
                        hours = hours + '; ' + 'Fri: ' + item.split('"hoursfri":"')[1].split('"')[0]
                        hours = hours + '; ' + 'Sat: ' + item.split('"hourssat":"')[1].split('"')[0]
                        hours = hours + '; ' + 'Sun: ' + item.split('"hourssunday":"')[1].split('"')[0]
                        country = item.split('"country":"')[1].split('"')[0]
                        typ = 'Store'
                        store = item.split('"clientkey":"')[1].split('"')[0]
                        lat = item.split('"latitude":"')[1].split('"')[0]
                        lng = item.split('"longitude":"')[1].split('"')[0]
                        yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
