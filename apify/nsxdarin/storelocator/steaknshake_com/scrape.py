import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests
import json

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
    url = 'https://www.steaknshake.com/wp-admin/admin-ajax.php?action=get_location_data_from_plugin'
    r = session.get(url, headers=headers)
    for item in json.loads(r.content):
        store = item['brandChainId']
        name = item['name']
        if 'phone1' in item:
            phone = item['phone1']
        else:
            phone = '<MISSING>'
        purl = 'https://www.steaknshake.com/locations/' + item['slug']
        try:
            hours = str(item).split("u'hours': {u'")[2].split('}')[0].replace("u'",'').replace("'",'')
        except:
            hours = '<MISSING>'
        add = item['address']['address1']
        if 'address2' in item['address']:
            add = add + ' ' + item['address']['address2']
        city = item['address']['city']
        zc = item['address']['zip']
        state = item['address']['region']
        country = item['address']['country']
        website = 'steaknshake.com'
        typ = 'Restaurant'
        if 'loc' in item['address']:
            lat = item['address']['loc'][0]
            lng = item['address']['loc'][1]
        else:
            lat = '<MISSING>'
            lng = '<MISSING>'
        if phone == '':
            phone = '<MISSING>'
        if lat == '':
            lat = '<MISSING>'
            lng = '<MISSING>'
        yield [website, purl, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
