import csv
from sgrequests import SgRequests

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    url = 'https://deltaco.com/index.php?page=locations'
    payload = {'q': '90210',
               'distance': '15000'
               }
    r = session.post(url, headers=headers, data=payload)
    for line in r.iter_lines():
        line = str(line.decode('utf-8'))
        if '<li id="store_item_' in line:
            lat = line.split('"latlng":{"lat":')[1].split(',')[0]
            lng = line.split('"lng":')[1].split('}')[0]
            name = line.split('"tags":"')[1].split('"')[0]
            typ = 'Restaurant'
            website = 'deltaco.com'
            country = 'US'
            phone = ''
            hours = ''
            store = 'Del Taco'
        if "<span class='day'>" in line:
            days = line.split("<span class='day'>")
            for day in days:
                if '<span class="hours' in day:
                    if hours == '':
                        hours = day.split('<')[0] + ' ' + day.split('<span class="hours')[1].split('">')[1].split('<')[0].strip()
                    else:
                        hours = hours + '; ' + day.split('<')[0] + ' ' + day.split('<span class="hours')[1].split('">')[1].split('<')[0].strip()
        if '<h4 class="store-info-location-address body-font black-text">' in line:
            add = line.split('<h4 class="store-info-location-address body-font black-text">')[1].split('<')[0]
            city = line.split('<br/>')[1].split(',')[0]
            state = line.split('<br/>')[1].split(',')[1].strip().split(' ')[0]
            zc = line.split('<br/>')[1].split(',')[1].strip().split(' ')[1].split('<')[0]
        if '</span><a href="tel:' in line:
            phone = line.split('</span><a href="tel:')[1].split('"')[0][:14]
        if '<a href="https://maps.google.com' in line:
            if hours == '':
                hours = '<MISSING>'
            if phone == '':
                phone = '<MISSING>'
            if '208 N Perkins Rd' in add:
                zc = '74075'
            yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
