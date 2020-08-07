import csv
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
    locs = []
    url = 'https://www.showcasecinemas.co.uk/cinemas/'
    r = session.get(url, headers=headers)
    website = 'showcasecinemas.co.uk'
    country = 'GB'
    hours = '<MISSING>'
    typ = '<MISSING>'
    for line in r.iter_lines():
        line = str(line.decode('utf-8'))
        if '{"CinemaId":' in line:
            items = line.split('{"CinemaId":')
            for item in items:
                if '"CinemaName":"' in item:
                    name = item.split('"CinemaName":"')[1].split('"')[0]
                    store = item.split(',')[0]
                    loc = 'https://www.showcasecinemas.co.uk' + item.split('"TheaterInfoUrl":"')[1].split('"')[0]
                    add = item.split('"Address1":"')[1].split('"')[0] + ' ' + item.split('"Address2":"')[1].split('"')[0]
                    add = add.strip()
                    city = item.split('"City":"')[1].split('"')[0]
                    state = item.split('"StateCode":"')[1].split('"')[0]
                    zc = item.split('"ZipCode":"')[1].split('"')[0]
                    lat = item.split(',"Latitude":"')[1].split('"')[0]
                    lng = item.split('"Longitude":"')[1].split('"')[0]
                    phone = '<MISSING>'
                    if city == '':
                        city = '<MISSING>'
                    if state == '':
                        state = '<MISSING>'
                    yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
