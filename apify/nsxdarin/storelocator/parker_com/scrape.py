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
    url = 'https://www.parker.com/parker/ParkerStoreRedesign/jsp/googlemaplink.jsp?localeCode=EN&searchType=N&distributorType=P&countryName=&from=parkerstore&countrySelect=USA&City=&County=&postalcode=10002&distance=10000'
    r = session.get(url, headers=headers)
    if r.encoding is None: r.encoding = 'utf-8'
    website = 'parker.com'
    Found = False
    for line in r.iter_lines(decode_unicode=True):
        if ',markers: [{' in line and Found is False:
            Found = True
            items = line.split('latitude:')
            for item in items:
                if 'longitude:' in item:
                    loc = '<MISSING>'
                    count = item.split('</b><br>')[1].split('<br>UNITED STATES')[0].count('<br>')
                    lat = item.split(',')[0]
                    lng = item.split('longitude:')[1].split(',')[0]
                    name = item.split('html:"<b>')[1].split('<')[0]
                    if count == 1:
                        add = item.split('<br>')[1]
                        csz = item.split('<br>')[2]
                        zc = csz.rsplit(' ',1)[1]
                        state = csz.rsplit(' ',2)[1].split(' ')[0]
                        city = csz.rsplit(' ',2)[0]
                    else:
                        add = item.split('<br>')[1] + ' ' + item.split('<br>')[2]
                        csz = item.split('<br>')[3]
                        zc = csz.rsplit(' ',1)[1]
                        state = csz.rsplit(' ',2)[1].split(' ')[0]
                        city = csz.rsplit(' ',2)[0]
                    country = 'US'
                    try:
                        phone = item.split('Telephone:')[1].split('<')[0]
                    except:
                        phone = '<MISSING>'
                    typ = '<MISSING>'
                    hours = '<MISSING>'
                    store = '<MISSING>'
                    yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
