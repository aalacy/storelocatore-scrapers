import csv
from sgrequests import SgRequests

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
           'content-type': 'application/x-www-form-urlencoded; charset=UTF-8'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    locs = []
    url = 'https://www.zxbrandedfuels.com/locations'
    payload = {'searchzip': 'Kansas City, MO, USA',
               'task': 'search',
               'radius': '-1',
               'option': 'com_mymaplocations',
               'limit': '0',
               'component': 'com_mymaplocations',
               'Itemid': '147',
               'zoom': '9',
               'format': 'json',
               'geo': '',
               'limitstart': '0'
               }

    r = session.post(url, headers=headers, data=payload)
    for line in r.iter_lines():
        line = str(line.decode('utf-8'))
        if '"name":"' in line:
            items = line.split('"name":"')
            for item in items:
                if "class='mytool'>" in item:
                    website = 'zxbrandedfuels.com'
                    country = 'US'
                    name = item.split('"')[0]
                    loc = 'https://zxbrandedfuels.com' + item.split('"url":"\\')[1].split('"')[0].replace('\\','')
                    add = item.split("'locationaddress'>")[1].split('<')[0]
                    city = item.split('<br\\/>')[1].split('&')[0]
                    state = item.split('<br\\/>')[1].split('&#44;')[1].split('<')[0]
                    zc = item.split('&nbsp;')[1].split('<')[0]
                    store = item.split('"itemid":')[1].split(',')[0]
                    typ = '<MISSING>'
                    lat = item.split('getUIDirection_side(')[1].split(',')[1].replace('\\','').replace('"','')
                    lng = item.split('getUIDirection_side(')[1].split(',')[2].split('\\')[0]
                    phone = '<MISSING>'
                    hours = '<MISSING>'
                    yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
