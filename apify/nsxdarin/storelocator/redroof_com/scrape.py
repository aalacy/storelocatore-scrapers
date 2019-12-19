import csv
import urllib2
import requests
import os

requests.packages.urllib3.disable_warnings()

session = requests.Session()
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
}

proxy_password = os.environ["PROXY_PASSWORD"]
proxy_url = "http://auto:{}@proxy.apify.com:8000/".format(proxy_password)
proxies = {
    'http': proxy_url,
    'https': proxy_url
}
session.proxies = proxies

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    url = 'https://www.redroof.com/sitemap.xml'
    locs = []
    r = session.get(url, headers=headers, verify=False)
    for line in r.iter_lines():
        if 'https://www.redroof.com/property/' in line:
            lurl = line.split('<loc>')[1].split('<')[0]
            locs.append(lurl)
    print('Found %s Locations.' % str(len(locs)))
    for loc in locs:
        if '-CA/' in loc:
            country = 'CA'
        else:
            country = 'US'
        name = ''
        add = ''
        city = ''
        state = ''
        zc = ''
        phone = ''
        website = 'redroof.com'
        typ = '<MISSING>'
        lat = '<MISSING>'
        lng = '<MISSING>'
        hours = '<MISSING>'
        store = loc.rsplit('/',1)[1]
        r2 = session.get(loc, headers=headers, verify=False)
        for line2 in r2.iter_lines():
            if 'name="og:title" content="' in line2:
                try:
                    name = line2.split(' | ')[1].split('"')[0]
                except:
                    name = 'Red Roof Inn'
            if 'property="s:streetAddress" content="' in line2:
                add = line2.split('property="s:streetAddress" content="')[1].split('"')[0]
            if 'property="s:addressLocality" content="' in line2:
                city = line2.split('property="s:addressLocality" content="')[1].split('"')[0]
            if 'property="s:addressRegion" content="' in line2:
                state = line2.split('property="s:addressRegion" content="')[1].split('"')[0]
            if 'property="s:postalCode" content="' in line2:
                zc = line2.split('property="s:postalCode" content="')[1].split('"')[0]
            if 'itemprop="telephone">' in line2:
                phone = line2.split('itemprop="telephone">')[1].split('<')[0]
        if 'Red Roof' not in name:
            name = 'Red Roof Inn'
        if 'PLUS+' in name:
            typ = 'Red Room PLUS+'
        else:
            typ = 'Red Roof Inn'
        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
