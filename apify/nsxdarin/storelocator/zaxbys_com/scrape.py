import csv
import urllib2
from sgrequests import SgRequests

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    states = []
    locs = []
    url = 'https://www.zaxbys.com/locations/'
    r = session.get(url, headers=headers)
    Found = False
    for line in r.iter_lines():
        if 'SELECT STATE</option>' in line:
            Found = True
        if Found and '</select>' in line:
            Found = False
        if Found and '<option value="' in line and '<option value=""' not in line:
            states.append('https://www.zaxbys.com/locations/' + line.split('value="')[1].split('"')[0])
    for state in states:
        print('Pulling State %s...' % state)
        r2 = session.get(state, headers=headers)
        for line2 in r2.iter_lines():
            if 'var locations = ' in line2:
                items = line2.split('"LongDisplay":"')
                for item in items:
                    if ',"OnlineOrdering":"' in item:
                        typ = 'Restaurant'
                        website = 'zaxbys.com'
                        add = item.split('"Address":"')[1].split('"')[0]
                        name = add
                        city = item.split('"Locality":"')[1].split('"')[0]
                        state = item.split('"Region":"')[1].split('"')[0]
                        zc = item.split('"Postcode":"')[1].split('"')[0]
                        try:
                            phone = item.split('"Phone":"')[1].split('"')[0]
                        except:
                            phone = '<MISSING>'
                        lat = item.split('"Latitude":"')[1].split('"')[0]
                        lng = item.split('"Longitude":"')[1].split('"')[0]
                        store = item.split('"StoreID":"')[1].split('"')[0]
                        hours = item.split('"StoreHours":')[1].split('","')[0]
                        country = 'US'
                        loc = item.split('"Website":"')[1].split('"')[0]
                        hours = hours.replace('";','"')
                        hours = hours.replace('"1,','Mon: ')
                        hours = hours.replace('"2,','Tue: ')
                        hours = hours.replace('"3,','Wed: ')
                        hours = hours.replace('"4,','Thu: ')
                        hours = hours.replace('"5,','Fri: ')
                        hours = hours.replace('"6,','Sat: ')
                        hours = hours.replace('"7,','Sun: ')
                        try:
                            status = item.split('"StoreStatus":"')[1].split('"')[0]
                        except:
                            status = '0'
                        hours = hours.replace(';1,','; Mon: ').replace(';2,','; Tue: ').replace(';3,','; Wed: ').replace(';4,','; Thu: ').replace(';5,','; Fri: ').replace(';6,','; Sat: ').replace(';7,','; Sun: ')
                        if ':' not in hours:
                            hours = '<MISSING>'
                        if 'http' not in loc:
                            loc = '<MISSING>'
                        if status == '1':
                            yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
