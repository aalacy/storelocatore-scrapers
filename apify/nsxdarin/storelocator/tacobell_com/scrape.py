import csv
import urllib2
import requests
import json
import os
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

requests.packages.urllib3.disable_warnings()

def requests_retry_session(
    retries=3,
    backoff_factor=0.3,
    status_forcelist=(500, 502, 504)
):
    session = requests.Session()
    proxy_password = os.environ["PROXY_PASSWORD"]
    proxy_url = "http://auto:{}@proxy.apify.com:8000/".format(proxy_password)
    proxies = {
        'http': proxy_url,
        'https': proxy_url
    }
    session.proxies = proxies
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

session = requests_retry_session()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
           'content-type': 'application/json',
           'X-Requested-With': 'XMLHttpRequest'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    locs = []
    url = 'https://www.tacobell.com/sitemap/Category-en-USD-0.xml'
    r = session.get(url, headers=headers, verify=False)
    for line in r.iter_lines():
        if '<loc>https://www.tacobell.com/food?store=' in line:
            sid = line.split('store=')[1].split('<')[0]
            if sid not in locs:
                locs.append(sid)
    url = 'https://www.tacobell.com/sitemap/Category-en-USD-1.xml'
    r = session.get(url, headers=headers, verify=False)
    for line in r.iter_lines():
        if '<loc>https://www.tacobell.com/food?store=' in line:
            sid = line.split('store=')[1].split('<')[0]
            if sid not in locs:
                locs.append(sid)    
    for loc in locs:
        PFound = True
        while PFound:
            try:
                PFound = False
                website = 'tacobell.com'
                typ = 'Restaurant'
                name = ''
                add = ''
                city = ''
                state = ''
                zc = ''
                country = 'US'
                store = loc
                phone = ''
                hours = ''
                lat = ''
                lng = ''
                lurl = 'https://locations.tacobell.com/' + loc
                r2 = session.get(lurl, headers=headers, verify=False)
                for line2 in r2.iter_lines():
                    if 'property="og:title" content="' in line2:
                        name = line2.split('property="og:title" content="')[1].split(' |')[0]
                        add = line2.split('<span class="c-address-street-1">')[1].split('<')[0].strip()
                        city = line2.split('<span class="c-address-city">')[1].split('<')[0]
                        state = line2.split('itemprop="addressRegion">')[1].split('<')[0]
                        zc = line2.split('itemprop="postalCode">')[1].split('<')[0].strip()
                        phone = line2.split('itemprop="telephone" id="phone-main">')[1].split('<')[0]
                        lat = line2.split('<meta itemprop="latitude" content="')[1].split('"')[0]
                        lng = line2.split('<meta itemprop="longitude" content="')[1].split('"')[0]
                        hrs = line2.split('Restaurant Hours</h2>')[1].split("}]' data-")[0]
                        days = hrs.split('"day":"')
                        for day in days:
                            if '"intervals":' in day:
                                if hours == '':
                                    try:
                                        hours = day.split('"')[0] + ': ' + day.split('"start":')[1].split('}')[0] + '-' + day.split('"end":')[1].split(',')[0]
                                    except:
                                        pass
                                else:
                                    try:
                                        hours = hours + '; ' + day.split('"')[0] + ': ' + day.split('"start":')[1].split('}')[0] + '-' + day.split('"end":')[1].split(',')[0]
                                    except:
                                        pass
                if hours == '':
                    hours = '<MISSING>'
                if lat == '':
                    lat = '<MISSING>'
                if lng == '':
                    lng = '<MISSING>'
                if name != '':
                    yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
            except:
                PFound = True

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
