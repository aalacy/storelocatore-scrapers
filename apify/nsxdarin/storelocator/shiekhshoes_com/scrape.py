import csv
import urllib2
from sgrequests import SgRequests
import time

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
           'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
           'cache-control': 'max-age=0',
           'referer': 'https://www.shiekh.com/storelocator/',
           'authority': 'www.shiekh.com',
           'method': 'GET',
           'scheme': 'https',
           'cookie': 'PHPSESSID=cmjsgg6920r4n4bvis3p2ge5f3; _ga=GA1.2.558095332.1568393503; _gid=GA1.2.609363746.1568393503; zaius_js_version=2.13.0; z_idsyncs=; vtsrc=source%3Ddirect%7Cmedium%3Dnone; _ju_v=4.1_2.58; mage-translation-storage=%7B%7D; mage-translation-file-version=%7B%7D; _ju_dn=1; mage-cache-storage=%7B%7D; mage-cache-storage-section-invalidation=%7B%7D; _fbp=fb.1.1568393503392.1359197611; zaius_web_push=; __adroll_fpc=fca14d24bcc26ca6fec3d6e3e4508d7a-s2-1568393503943; _ju_dc=ce45d49a-d646-11e9-b12e-5bb8537a070f; sellerData=%7B%7D; __hstc=155523684.61b34fb41702834a0f74466eccd6abdc.1568393505432.1568393505432.1568393505432.1; hubspotutk=61b34fb41702834a0f74466eccd6abdc; __hssrc=1; mage-cache-sessid=true; form_key=fdikWPetP7SOj1HO; _gat_UA-85349200-1=1; vuid=3fdb5249-4fc3-4060-b87a-680be86aeb57%7C1568394081239; _derived_epik=dj0yJnU9Wm4zdEJQSmlWMUJOTjNBT2djQWVFR0JycmFTVkw1YUQmbj1nWmM5SXNFZzF0N3FWU1FyWUpiWWFBJm09NyZ0PUFBQUFBRjE3eTNJ; __ar_v4=3WA4URD6FNAN3BNV5HGQGC%3A20190913%3A11%7CELELR4V2GRBC7FAEL3AIZ3%3A20190913%3A11%7CTTUBM64SQBGSPD2AII6ZUB%3A20190913%3A11; _ju_pn=11; _px2=eyJ1IjoiMWMzNjIyOTAtZDY0OC0xMWU5LTkxZTItOWY1ODI4NmE2MzE1IiwidiI6ImE0MTA4ODcwLWI4MjAtMTFlNi05MGQwLWI3ODVhMjBiYjRhOCIsInQiOjE1NjgzOTQ1OTg3NjksImgiOiJlMTQ0MjNkZjg2ZTc4MTliZDVhOWM3M2UwYjI1Mzk3ZjllYWY2MTA4YTg3MWJlM2YxMWIwZWIwMWUzYWQ5ZmU3In0=; __hssc=155523684.10.1568393505433; sc_fb_session={%22start%22:1568393505536%2C%22p%22:11}; sc_fb={%22v%22:0.3%2C%22t%22:85%2C%22p%22:11%2C%22s%22:1%2C%22b%22:[]%2C%22pv%22:[]%2C%22tr%22:0%2C%22e%22:[]}'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    url = 'https://www.shiekh.com/store-list'
    locs = []
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if '<a class="brand-item-link" href="https://www.shiekh.com/stores/' in line:
            lurl = line.split('href="')[1].split('"')[0]
            if 'online-store' not in line:
                locs.append(lurl)
    for loc in locs:
        name = ''
        add = ''
        city = ''
        state = ''
        lat = ''
        lng = ''
        hours = ''
        zc = '<MISSING>'
        phone = ''
        print('Pulling Location %s...' % loc)
        website = 'shiekhshoes.com'
        typ = 'Store'
        store = ''
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            if '<title>' in line2:
                name = line2.split('>')[1].split('<')[0].strip()
            if '<p itemprop="streetAddress"' in line2:
                add = line2.split('>')[1].split('<')[0].strip()
            if '"address":"' in line2:
                phone = line2.split('"phone":"')[1].split('"')[0]
                lat = line2.split('"latitude":"')[1].split('"')[0]
                lng = line2.split('"longitude":"')[1].split('"')[0]
                store = line2.split('"storelocator_id":"')[1].split('"')[0]
            if '<span itemprop="addressLocality">' in line2:
                city = line2.split('<span itemprop="addressLocality">')[1].split('<')[0]
            if '<span itemprop="addressRegion">' in line2:
                state = line2.split('<span itemprop="addressRegion">')[1].split('<')[0]
            if 'itemprop="openingHours" content="' in line2:
                hrs = line2.split('itemprop="openingHours" content="')[1].split('"')[0]
                if hours == '':
                    hours = hrs
                else:
                    hours = hours + '; ' + hrs
        country = 'US'
        if phone == '':
            phone = '<MISSING>'
        if hours == '':
            hours = '<MISSING>'
        if '404 Not Found' not in name:
            yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
        time.sleep(3)

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
