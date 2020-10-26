import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests
import json
from sgzip import sgzip
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('nike_com')




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
    ids = []
    for coord in sgzip.coords_for_radius(50):
        x = coord[0]
        y = coord[1]
        logger.info(('Pulling Lat-Long %s,%s...' % (str(x), str(y))))
        url = 'https://nike.brickworksoftware.com/locations_search?hitsPerPage=50&page=1&getRankingInfo=true&facets[]=*&aroundRadius=all&filters=domain:nike.brickworksoftware.com+AND+publishedAt%3C%3D1578345837793&esSearch=%7B%22page%22:0,%22storesPerPage%22:50,%22domain%22:%22nike.brickworksoftware.com%22,%22locale%22:%22en_US%22,%22must%22:[%7B%22type%22:%22range%22,%22field%22:%22published_at%22,%22value%22:%7B%22lte%22:1578345837793%7D%7D],%22filters%22:[],%22aroundLatLng%22:%7B%22lat%22:' + str(x) + ',%22lon%22:' + str(y) + '%7D%7D'
        r = session.get(url, headers=headers)
        if r.encoding is None: r.encoding = 'utf-8'
        for line in r.iter_lines(decode_unicode=True):
            if '"_geoloc":' in line:
                items = line.split('"_geoloc":')
                for item in items:
                    if ',"status":"' in item:
                        website = 'nike.com'
                        typ = item.split('"parkingSuggestions"')[1].split('"type":"')[1].split('"')[0]
                        add = item.split('"address1":"')[1].split('"')[0]
                        try:
                            add = add + ' ' + item.split('"address2":"')[1].split('"')[0]
                        except:
                            pass
                        city = item.split('"city":"')[1].split('"')[0]
                        try:
                            state = item.split('"state":"')[1].split('"')[0]
                        except:
                            state = '<MISSING>'
                        hours = ''
                        country = item.split('"countryCode":"')[1].split('"')[0]
                        try:
                            phone = item.split('"phoneNumber":"')[1].split('"')[0]
                        except:
                            phone = '<MISSING>'
                        try:
                            zc = item.split('"postalCode":"')[1].split('"')[0]
                        except:
                            zc = '<MISSING>'
                        purl = 'https://www.nike.com/us/retail/s/' + item.split('"slug":"')[1].split('"')[0]
                        name = item.split('"name":"')[1].split('"')[0]
                        lat = item.split('"latitude":')[1].split(',')[0]
                        lng = item.split('"longitude":')[1].split(',')[0]
                        try:
                            store = item.split('"id":')[1].split(',')[0]
                        except:
                            store = '<MISSING>'
                        days = item.split('"hours":[')[1].split('}],"departments"')[0].split('"type":"')
                        for day in days:
                            if '"startTime":"' in day:
                                hrs = day.split('"displayDay":"')[1].split('"')[0] + ': ' + day.split(',"displayStartTime":"')[1].split('"')[0].strip() + '-' + day.split(',"displayEndTime":"')[1].split('"')[0].strip()
                                if hours == '':
                                    hours = hrs
                                else:
                                    hours = hours + '; ' + hrs
                        if store not in ids:
                            if country == 'US':
                                ids.append(store)
                                yield [website, purl, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
