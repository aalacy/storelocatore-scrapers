import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests
import json

session = SgRequests()
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'}

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "operating_info", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    locs = []
    url = 'https://wafflehouse.locally.com/stores/conversion_data?has_data=true&company_id=117995&store_mode=&style=&color=&upc=&category=&inline=1&show_links_in_list=&parent_domain=&map_center_lat=40&map_center_lng=-95&map_distance_diag=1000000&sort_by=proximity&no_variants=0&only_retailer_id=&dealers_company_id=&only_store_id=false&uses_alt_coords=false&q=false&zoom_level=4'
    r = session.get(url, headers=headers, stream=True)
    for item in json.loads(r.content)['markers']:
        opinfo = '<MISSING>'
        name = item['name']
        store = item['id']
        add = item['address']
        if "u'isClosed': True" in str(item):
            opinfo = 'TEMPORARILY CLOSED'
        city = item['city']
        state = item['state']
        zc = item['zip']
        phone = item['phone']
        lat = item['lat']
        lng = item['lng']
        country = 'US'
        website = 'wafflehouse.com'
        typ = 'Restaurant'
        hours = 'Mon-Sun: 24 Hours'
        loc = '<MISSING>'
        yield [website, loc, name, opinfo, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
