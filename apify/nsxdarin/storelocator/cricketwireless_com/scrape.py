import csv
import urllib2
import requests
import json

session = requests.Session()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    alllocs = []
    states = []
    url = 'https://momentfeed-prod.apigee.net/lf/directory/counts?accountId=5367f3a1ef070044f1418f27&country=US'
    r = session.get(url, headers=headers)
    for item in json.loads(r.content)['counts']:
        states.append(item['name'])
    for state in states:
        sc = 0
        cities = []
        print('Pulling State %s...' % state)
        url2 = 'https://momentfeed-prod.apigee.net/lf/directory/counts?accountId=5367f3a1ef070044f1418f27&country=US&region=' + state
        r2 = session.get(url2, headers=headers)
        for item2 in json.loads(r2.content)['counts']:
            cities.append(item2['name'])
        for city in cities:
            locs = []
            #print('Pulling City %s...' % city)
            url3 = 'https://momentfeed-prod.apigee.net/lf/directory/locations?accountId=5367f3a1ef070044f1418f27&country=US&locality=' + city.replace(' ','+') + '&region=' + state
            r3 = session.get(url3, headers=headers)
            try:
                for item3 in json.loads(r3.content)['locations']:
                    lurl = item3['llpUrl']
                    if lurl not in alllocs:
                        alllocs.append(lurl)
                        locs.append(item3['storeInfo']['address'])
                for loc in locs:
                    #print('Pulling Location %s...' % loc)
                    url4 = 'https://momentfeed-prod.apigee.net/api/llp/cricket.json?address=' + loc.replace(' ','+') + '&auth_token=IVNLPNUOBXFPALWE&locality=' + city.replace(' ','+') + '&multi_account=false&pageSize=1&region=' + state
                    r4 = session.get(url4, headers=headers)
                    name = ''
                    website = 'cricketwireless.com'
                    loc = ''
                    add = ''
                    city = ''
                    state = ''
                    zc = ''
                    country = 'US'
                    store = ''
                    typ = ''
                    lat = ''
                    lng = ''
                    hours = ''
                    purl = ''
                    lines = r4.iter_lines()
                    name = 'Cricket Wireless Authorized Retailer'
                    for line in lines:
                        if '"corporate_id": "' in line:
                            store = line.split('"corporate_id": "')[1].split('"')[0]
                        if add == '' and '"address": "' in line:
                            add = line.split('"address": "')[1].split('"')[0]
                        if '"address_extended": "' in line:
                            add = add + ' ' + line.split('"address_extended": "')[1].split('"')[0]
                            add = add.strip()
                        if '"locality": "' in line:
                            city = line.split('"locality": "')[1].split('"')[0]
                        if '"region": "' in line:
                            state = line.split('"region": "')[1].split('"')[0]
                        if '"postcode": "' in line:
                            zc = line.split('"postcode": "')[1].split('"')[0]
                        if '"phone": "' in line:
                            phone = line.split('"phone": "')[1].split('"')[0]
                        if '"llp_url": "' in line:
                            purl = 'https://www.cricketwireless.com/stores' + line.split('"llp_url": "')[1].split('"')[0]
                        if '"latitude": "' in line:
                            lat = line.split('"latitude": "')[1].split('"')[0]
                        if '"longitude": "' in line:
                            lng = line.split('"longitude": "')[1].split('"')[0]
                        if typ == '' and '"store_info": {' in line:
                            typ = next(lines).split('"name": "')[1].split('"')[0]
                        if hours == '' and '"store_hours": "' in line:
                            hours = line.split('"store_hours": "')[1].split('"')[0]
                            hours = hours.replace('1,','Mon: ').replace(';2,','; Tue: ')
                            hours = hours.replace(';2,','; Tue: ')
                            hours = hours.replace(';3,','; Wed: ')
                            hours = hours.replace(';4,','; Thu: ')
                            hours = hours.replace(';5,','; Fri: ')
                            hours = hours.replace(';6,','; Sat: ')
                            hours = hours.replace(';7,','; Sun: ')
                            hours = hours.replace(',','-')
                    if hours == '':
                        hours = '<MISSING>'
                    if phone == '':
                        phone = '<MISSING>'
                    sc = sc + 1
                    yield [website, purl, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
            except:
                pass
        print('%s Total In %s...' % (str(sc), state))
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
