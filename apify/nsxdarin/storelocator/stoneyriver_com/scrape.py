import csv
import urllib.request, urllib.error, urllib.parse
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
    url = 'https://stoneyriver.com/locations/'
    r = session.get(url, headers=headers)
    if r.encoding is None: r.encoding = 'utf-8'
    lines = r.iter_lines(decode_unicode=True)
    HoursFound = False
    for line in lines:
        if 'Book Now <span class="screenreadable">' in line:
            name = line.split('Book Now <span class="screenreadable">')[1].split('<')[0]
            HoursFound = False
            website = 'stoneyriver.com'
            typ = name.split(' |')[0]
            country = 'US'
            hours = ''
            store = line.split('{"venueId":')[1].split(',')[0]
        if 'google.com/maps/' in line or 'maps.google.com/' in line:
            if '/@' in line:
                lat = line.split('/@')[1].split(',')[0]
                lng = line.split('/@')[1].split(',')[1]
            else:
                try:
                    lat = line.split('sll=')[1].split(',')[0]
                    lng = line.split('sll=')[1].split(',')[1].split('&')[0]
                except:
                    lat = '<MISSING>'
                    lng = '<MISSING>'
        if '<address>' in line:
            add = line.split('<address>')[1].split('</a><br />')[0].split('<')[0]
            city = line.split('<address>')[1].split('</a><br />')[0].rsplit('<br />',1)[1].split(',')[0]
            state = line.split('<address>')[1].split('</a><br />')[0].rsplit('<br />',1)[1].split(',')[1].rsplit(' ',1)[0].strip()
            zc = line.split('<address>')[1].split('</a><br />')[0].rsplit('<br />',1)[1].split(',')[1].rsplit(' ',1)[1].strip()
            phone = line.split('<a href="tel:')[1].split('"')[0]
            hours = line.split('Hours of Operation<br /><p>')[1].split('<')[0]
            g = next(lines)
            if '<span class="screenreadable">' not in g:
                hours = hours + '; ' + g.split('<')[0]
                g = next(lines)
            hours = hours + '; ' + g.split('<')[0]
            purl = '<MISSING>'
            yield [website, purl, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
