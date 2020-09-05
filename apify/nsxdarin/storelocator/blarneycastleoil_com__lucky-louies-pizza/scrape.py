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
    website = 'blarneycastleoil.com/lucky-louies-pizza'
    url = 'http://blarneycastleoil.com/ez-mart-promo/ez-mart-locations/'
    r = session.get(url, headers=headers)
    if r.encoding is None: r.encoding = 'utf-8'
    for line in r.iter_lines(decode_unicode=True):
        if 'maplistScriptParamsKo' in line:
            items = line.replace('"categories":[{"title":"','').split('{"title":"')
            for item in items:
                if 'maplistScriptParamsKo' not in item and 'address":"<p>' in item:
                    country = 'US'
                    state = 'MI'
                    name = item.split('"')[0]
                    store = '<MISSING>'
                    hours = '<MISSING>'
                    try:
                        lat = item.split('"latitude":"')[1].split('"')[0]
                        lng = item.split('"longitude":"')[1].split('"')[0]
                    except:
                        lat = '<MISSING>'
                        lng = '<MISSING>'
                    addinfo = item.split('address":"<p>')[1].split('<\\/p>')[0]
                    if addinfo.count('<br \\/>\\n') == 4:
                        add = addinfo.split('<br \\/>\\n')[1]
                        city = addinfo.split('<br \\/>\\n')[2]
                        zc = addinfo.split('<br \\/>\\n')[3]
                    if addinfo.count('<br \\/>\\n') == 3:
                        add = addinfo.split('<br \\/>\\n')[0]
                        city = addinfo.split('<br \\/>\\n')[1]
                        zc = addinfo.split('<br \\/>\\n')[2]
                    loc = '<MISSING>'
                    typ = '<MISSING>'
                    phone = '<MISSING>'
                    yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
