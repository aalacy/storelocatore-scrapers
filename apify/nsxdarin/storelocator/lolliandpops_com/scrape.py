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
    url = 'https://www.lolliandpops.com/pages/stores'
    r = session.get(url, headers=headers)
    website = 'lolliandpops.com'
    typ = '<MISSING>'
    country = 'US'
    loc = '<MISSING>'
    store = '<MISSING>'
    hours = '<MISSING>'
    lat = '<MISSING>'
    lng = '<MISSING>'
    for line in r.iter_lines():
        line = str(line.decode('utf-8'))
        if '{\\"name\\":\\"' in line:
            items = line.split('{\\"name\\":\\"')
            for item in items:
                if '\\"address\\"' in item:
                    name = item.split('\\"')[0]
                    add = item.split('"address\\":\\"')[1].split('\\')[0]
                    city = item.split('"city\\":\\"')[1].split('\\')[0]
                    state = item.split('"state_code\\":\\"')[1].split('\\')[0]
                    zc = item.split('"zip\\":\\"')[1].split('\\')[0]
                    phone = item.split('phone\\":\\"')[1].split('\\')[0]
                    try:
                        lat = item.split('\\/@')[1].split(',')[0]
                        lng = item.split('\\/@')[1].split(',')[1]
                    except:
                        lat = '<MISSING>'
                        lng = '<MISSING>'
                    if '\\"mon_fri_hours\\":\\"' in item:
                        hours = item.split('\\"mon_fri_hours\\":\\"')[1].split('\\')[0]
                        try:
                            hours = hours + '; ' + item.split('"weekend_hours\\":\\"')[1].split('\\')[0]
                        except:
                            pass
                    else:
                        hours = '<MISSING>'
                    yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
