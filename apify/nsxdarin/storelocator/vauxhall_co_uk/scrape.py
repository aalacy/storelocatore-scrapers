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
    url = 'https://www.vauxhall.co.uk/apps/atomic/DealersServlet?distance=1000&latitude=55.378051&longitude=-3.435973&maxResults=1000&path=L2NvbnRlbnQvdmF1eGhhbGwvd29ybGR3aWRlL3VrL2Vu&searchType=latlong'
    r = session.get(url, headers=headers)
    if r.encoding is None: r.encoding = 'utf-8'
    for line in r.iter_lines(decode_unicode=True):
        if '{"siteGeo":"' in line:
            items = line.split('{"siteGeo":"')
            for item in items:
                if '"generalOpeningHour":"' in item:
                    website = 'vauxhall.co.uk'
                    loc = '<MISSING>'
                    name = item.split('"dealerName":"')[1].split('"')[0]
                    country = 'GB'
                    hours = item.split('"generalOpeningHour":"')[1].split(',"dealerName":"')[0].replace('<br />"','"').split('"')[0].replace('<br />','; ')
                    zc = item.split(',"postalCode":"')[1].split('"')[0]
                    lat = item.split('{"latitude":"')[1].split('"')[0]
                    lng = item.split(',"longitude":"')[1].split('"')[0]
                    phone = item.split('"phone1":"')[1].split('"')[0]
                    if hours == '':
                        hours = '<MISSING>'
                    city = item.split('"cityName":"')[1].split('"')[0]
                    add = item.split('"addressLine1":"')[1].split('"')[0]
                    state = item.split('"county":"')[1].split('"')[0]
                    if state == '':
                        state = '<MISSING>'
                    store = item.split('"')[0]
                    typ = '<MISSING>'
                    yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
