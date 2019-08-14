import csv
import urllib2
import requests

session = requests.Session()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    url = 'https://stoneyriver.com/locations/'
    r = session.get(url, headers=headers)
    lines = r.iter_lines()
    HoursFound = False
    for line in lines:
        if '<h4 class="accordionButton">' in line:
            HoursFound = False
            name = line.split('" >')[1].split('<')[0].strip()
            website = 'stoneyriver.com'
            add = ''
            city = ''
            state = ''
            zc = ''
            phone = ''
            hours = ''
            typ = 'Restaurant'
            store = ''
            country = 'US'
            lat = ''
            lng = ''
        if '{"venueId":' in line:
            store = line.split('{"venueId":')[1].split(',')[0]
        if 'google.com/maps/place/' in line:
            if '/@' in line:
                lat = line.split('/@')[1].split(',')[0]
                lng = line.split('/@')[1].split(',')[1]
            else:
                try:
                    lat = line.split('sll=')[1].split(',')[0]
                    lng = line.split('sll=')[1].split(',')[1].split('&')[0]
                except:
                    lat = ''
                    lng = ''
        if '<p><a href=' in line:
            add = line.split('"_blank"')[1].split('>')[1].split('<')[0].strip()
            g = next(lines)
            city = g.split(',')[0].strip().replace('\t','')
            if '      ' in city:
                add = add + ' ' + city.split('      ')[0]
                city = city.split('      ')[1]
            state = g.split(',')[1].strip().split('\t')[0]
            try:
                zc = g.split(',')[1].strip().split('<')[0].strip().replace('\t',' ').rsplit(' ',1)[1]
            except:
                zc = ''
        if 'strong>GM:' in line:
            phone = line.split('strong>GM:')[1].split('<br />')[1].split('<')[0].strip()
        if '<div class="locationSocial">' in line and 'Coming Soon' not in name:
            yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
        if 'Hours of Operation</strong>' in line:
            HoursFound = True
        if HoursFound and '</div>' in line:
            HoursFound = False
        if HoursFound and 'Hours of Operation</strong>' not in line:
            if hours == '':
                hours = line.split('<')[0].replace('<p>','').strip()
            else:
                hours = hours + '; ' + line.split('<')[0].replace('<p>','').strip()

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
