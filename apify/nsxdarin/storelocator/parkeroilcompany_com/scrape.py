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
    locs = []
    url = 'https://parkeroilcompany.com/about-us/office-locator/'
    r = session.get(url, headers=headers)
    if r.encoding is None: r.encoding = 'utf-8'
    for line in r.iter_lines(decode_unicode=True):
        if '<b>Distance:' in line:
            items = line.split("['")
            for item in items:
                if '<b>Distance:' in item:
                    lat = item.split("',")[1].split(',')[0].strip()
                    lng = item.split("',")[1].split(',')[1].strip()
                    website = 'parkeroilcompany.com'
                    loc = '<MISSING>'
                    addinfo = item.split('<b style="color:#003766;">')[1].split('<b>')[0]
                    name = addinfo.split('<')[0]
                    if addinfo.count('<br>') == 3:
                        add = addinfo.split('<br>')[1]
                        city = addinfo.split('<br>')[2].split(',')[0]
                        state = addinfo.split('<br>')[2].split(',')[1].strip().split(' ')[0]
                        zc = addinfo.split('<br>')[2].rsplit(' ',1)[1]
                    else:
                        add = addinfo.split('<br>')[1] + ' ' + addinfo.split('<br>')[2]
                        add = add.strip()
                        city = addinfo.split('<br>')[3].split(',')[0]
                        state = addinfo.split('<br>')[3].split(',')[1].strip().split(' ')[0]
                        zc = addinfo.split('<br>')[3].rsplit(' ',1)[1]
                    country = 'US'
                    store = '<MISSING>'
                    try:
                        phone = item.split('Phone:</b>')[1].split('<')[0].strip()
                    except:
                        phone = '<MISSING>'
                    typ = item.split('<b>Distance:</b>')[1].split(' Miles')[0].strip()
                    hours = '<MISSING>'
                    if 'Exxon' in typ:
                        typ = 'Exxon'
                    if 'Citgo' in typ:
                        typ = 'Citgo'
                    if 'Parker Oil' in typ:
                        typ = 'Parker Oil'
                    if 'Red Barn' in typ:
                        typ = 'Red Barn'
                    yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
