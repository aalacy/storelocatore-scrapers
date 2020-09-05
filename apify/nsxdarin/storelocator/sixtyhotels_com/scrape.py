import csv
import urllib.request, urllib.error, urllib.parse
import requests

session = requests.Session()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
           'content-type': 'application/json',
           'X-Requested-With': 'XMLHttpRequest'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    url = 'https://www.sixtyhotels.com/api/slides'
    r = session.get(url, headers=headers)
    if r.encoding is None: r.encoding = 'utf-8'
    for line in r.iter_lines(decode_unicode=True):
        if '"fieldgroup":"fieldgroup1","fieldgroup_label":null,"fieldgroupsub":null,"areaid":2,"parentid":2,"title":null,"active":true,"h1":"' in line:
            items = line.split('"fieldgroup":"fieldgroup1","fieldgroup_label":null,"fieldgroupsub":null,"areaid":2,"parentid":2,"title":null,"active":true,"h1":"')
            for item in items:
                if '{"code":"GET_SUCCESS",' not in item:
                    name = item.split('"')[0]
                    loc = '<MISSING>'
                    add = item.split('"h2":"')[1].split('"')[0]
                    csz = item.split('"h3":"')[1].split('"')[0]
                    zc = csz.rsplit(' ',1)[1].strip()
                    if 'new york' in csz:
                        city = 'New York'
                        state = 'NY'
                    if 'beverly' in csz:
                        city = 'Beverly Hills'
                        state = 'CA'
                    phone = item.split('"phone":"')[1].split('"')[0]
                    website = 'sixtyhotels.com'
                    hours = '<MISSING>'
                    store = '<MISSING>'
                    country = 'US'
                    typ = 'Hotel'
                    phone = item.split('"phone":"')[1].split('"')[0].replace('.','-')
                    if 'soho' in name.lower():
                        loc = 'https://www.sixtyhotels.com/destinations/new-york-city/sixty-soho'
                    if 'beverly' in name.lower():
                        loc = 'https://www.sixtyhotels.com/destinations/california/sixty-beverly-hills'
                    if 'les' in name.lower():
                        loc = 'https://www.sixtyhotels.com/destinations/new-york-city/sixty-les'
                    lat = item.split('!3d')[1].split('!')[0]
                    lng = item.split('!4d')[1].split('"')[0]
                    yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
