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
    for x in range(2000, 8000):
        print(x)
        url = 'https://www.tesco.com/store-locator/uk/?bid=' + str(x)
        r = session.get(url, headers=headers)
        Found = True
        website = 'tesco.com'
        name = ''
        add = ''
        loc = url
        city = ''
        state = '<MISSING>'
        zc = ''
        country = 'UK'
        store = str(x)
        phone = ''
        typ = '<MISSING>'
        lat = ''
        lng = ''
        hours = ''
        for line in r.iter_lines():
            if 'find any stores that match your search.' in line:
                Found = False
            if '"storeDetails":' in line:
                name = line.split('"name":"')[1].split('"')[0]
                addinfo = line.split('"address":"')[1].split('"')[0]
                if addinfo.count(',') == 3:
                    add = addinfo.split(',')[0].strip()
                    city = addinfo.split(',')[2].strip()
                    zc = addinfo.split(',')[3].strip()
                else:
                    add = addinfo.split(',')[0].strip()
                    city = addinfo.split(',')[1].strip()
                    zc = addinfo.split(',')[2].strip()
                phone = line.split('"tel":"')[1].split('"')[0]
                lat = line.split('"lat":')[1].split(',')[0]
                lng = line.split('"lng":')[1].split(',')[0]
                days = line.split('"openingHours":[')[1].split('}],"exceptions":')[0].split('"timing":"')
                for day in days:
                    if '"day":"' in day:
                        hrs = day.split('"day":"')[1].split('"')[0] + ': ' + day.split('"')[0]
                        if hours == '':
                            hours = hrs
                        else:
                            hours = hours + '; ' + hrs
        if hours == '':
            hours = '<MISSING>'
        if phone == '':
            phone = '<MISSING>'
        if Found:
            yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
