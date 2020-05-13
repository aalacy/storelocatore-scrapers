import csv
import os
from sgrequests import SgRequests
import sgzip

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

PATH_TEMPLATE = "/search?q={}&r=1000&per=50"
URL_TEMPLATE = 'https://locator.chick-fil-a.com.yext-cdn.com' + PATH_TEMPLATE

search = sgzip.ClosestNSearch()
search.initialize(country_codes = ['us'])


MAX_RESULTS = 50
MAX_DISTANCE = 20

session = SgRequests()

def get_headers(zc):
    return {
        'Authority': 'locator.chick-fil-a.com.yext-cdn.com',
        'Method': 'GET',
        #'Path': PATH_TEMPLATE.format(zc),
        'Scheme': 'https',
        'Accept': 'application/json',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
        #'Referrer': URL_TEMPLATE.format(zc),
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'
    }

COOKIES = {
    'UTMsessionStart': 'true',
    'emHashed': 'undefined',
    '_ga': 'GA1.2.422645551.1582838311',
    '_gid': 'GA1.2.1700769816.1582838311',
    '_mibhv': 'anon-1582838280841-7352020692_8351',
    '_micpn': 'esp:-1::1582838310656',
    '_derived_epik': 'dj0yJnU9QW44aWU5MTl5clNPUUR0TzRvMHpUUjI0eGUwbDBWOHImbj1BZVhNVmVoSC1TSHNWelozaE5VREFRJm09NyZ0PUFBQUFBRjVZTTFB'
}

def handle_missing(field):
    if field == None or (type(field) == type('x') and len(field.strip()) == 0):
        return '<MISSING>'
    return field

def fetch_data():
    keys = set()
    locations = []
    coord = search.next_zip()
    while coord:
        result_coords = []
        print("remaining zipcodes: " + str(len(search.zipcodes)))
        r = session.get(URL_TEMPLATE.format(coord), cookies=COOKIES, headers=get_headers(coord))
        for line in r.iter_lines():
            if '"profile":{' in line:
                items = line.split('"profile":{')
                for item in items:
                    if '"address":{"city":"' in item:
                        city = item.split('"address":{"city":"')[1].split('"')[0]
                        state = item.split('"region":"')[1].split('"')[0]
                        country = 'US'
                        website = 'chick-fil-a.com'
                        typ = 'Restaurant'
                        add = item.split('"line1":"')[1].split('"')[0]
                        zc = item.split('"postalCode":"')[1].split('"')[0]
                        name = item.split('"c_locationName":"')[1].split('"')[0]
                        store = item.split('"id":"')[1].split('"')[0]
                        try:
                            phone = item.split('"mainPhone":{"')[1].split('"display":"')[1].split('"')[0]
                        except:
                            phone = '<MISSING>'
                        loc = item.split('"websiteUrl":"')[1].split('"')[0]
                        lat = item.split('"lat":')[1].split(',')[0]
                        lng = item.split('"long":')[1].split('}')[0]
                        hours = ''
                        days = item.split('"normalHours":[')[1].split('"day":"')
                        for day in days:
                            if '"intervals":' in day:
                                if '"isClosed":true' in day:
                                    hrs = day.split('"')[0] + ': Closed'
                                else:
                                    hrs = day.split('"')[0] + ': ' + day.split('"start":')[1].split('}')[0] + '-' + day.split('"end":')[1].split(',')[0]
                                if hours == '':
                                    hours = hrs
                                else:
                                    hours = hours + '; ' + hrs
                        if store not in locations:
                            locations.append(store)
                            yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
        #print("max distance update")
        search.max_distance_update(MAX_DISTANCE)
        coord = search.next_zip()

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
