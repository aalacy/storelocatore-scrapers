import csv
import os
from sgrequests import SgRequests
import sgzip
import json
import time
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('subway_co_uk')



def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

search = sgzip.ClosestNSearch() # TODO: OLD VERSION [sgzip==0.0.55]. UPGRADE IF WORKING ON SCRAPER!
search.initialize(country_codes = ['gb'])

MAX_RESULTS = 250

session = SgRequests()

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'
           }

def fetch_data():
    ids = []
    locations = []
    coord = search.next_coord()
    while coord:
        time.sleep(1)
        result_coords = []
        logger.info(("remaining zipcodes: " + str(search.zipcodes_remaining())))
        x, y = coord[0], coord[1]
        url = 'https://locator-svc.subway.com/v3/GetLocations.ashx?callback=jQuery111103224152676024219_1577552416099&q=%7B%22InputText%22%3A%22' + str(x) + '%2C' + str(y) + '%22%2C%22GeoCode%22%3A%7B%22Latitude%22%3A' + str(x) + '%2C%22Longitude%22%3A' + str(y) + '%2C%22Accuracy%22%3Anull%2C%22CountryCode%22%3A%22%22%2C%22RegionCode%22%3Anull%2C%22PostalCode%22%3Anull%2C%22City%22%3Anull%2C%22LocalityType%22%3Anull%2C%22name%22%3Anull%7D%2C%22DetectedLocation%22%3A%7B%22Latitude%22%3A0%2C%22Longitude%22%3A0%2C%22Accuracy%22%3A0%7D%2C%22Paging%22%3A%7B%22StartIndex%22%3A1%2C%22PageSize%22%3A50%7D%2C%22ConsumerParameters%22%3A%7B%22metric%22%3Afalse%2C%22culture%22%3A%22en-GB%22%2C%22country%22%3A%22GB%22%2C%22size%22%3A%22D%22%2C%22template%22%3A%22%22%2C%22rtl%22%3Afalse%2C%22clientId%22%3A%2217%22%2C%22key%22%3A%22SUBWAY_PROD%22%7D%2C%22Filters%22%3A%5B%5D%2C%22LocationType%22%3A0%2C%22behavior%22%3A%22%22%2C%22FavoriteStores%22%3Anull%2C%22RecentStores%22%3Anull%2C%22Stats%22%3A%7B%22abc%22%3A%5B%7B%22N%22%3A%22geo%22%2C%22R%22%3A%22A%22%7D%5D%2C%22src%22%3A%22map%22%2C%22act%22%3A%22map%22%2C%22c%22%3A%22subwayLocator%22%7D%7D&_=1577552416106'
        r = session.get(url, headers=headers)
        ll = []
        for line in r.iter_lines(decode_unicode=True):
            if '{"LocationId":' in line:
                stores = line.split('"LocationId":{"')
                for snum in stores:
                    if '"Latitude":' in snum:
                        slat = snum.split('"Latitude":')[1].split(',')[0]
                        slng = snum.split('"Longitude":')[1].split(',')[0]
                        ll.append(snum.split('StoreNumber":')[1].split(',')[0] + '|' + slat + '|' + slng)
                items = line.split('<div class=\\"locatorMainInfo\\">')
                for item in items:
                    if '<div class=\\"storeMainAddressAndDistance\\"' in item:
                        add = item.split('storeMainAddress\\">            \\r\\n           <h3> ')[1].split('<')[0]
                        add = add + ' ' + item.split('locatorAddress2\\">')[1].split('<')[0]
                        add = add + ' ' + item.split('locatorAddress3\\">')[1].split('<')[0]
                        add = add.strip()
                        csz = item.split('<div class=\\"locatorAddressCityState\\">')[1].split('<')[0]
                        if csz.count(',') == 2:
                            city = csz.split(',')[0]
                            state = csz.split(',')[1].strip().split(' ')[0]
                            try:
                                zc = csz.split(',')[1].strip().split(' ',1)[1]
                            except:
                                zc = '<MISSING>'
                        else:
                            try:
                                city = csz.split(',')[1].strip()
                                state = csz.split(',')[2].strip().split(' ')[0]
                                zc = csz.split(',')[2].strip().split(' ',1)[1]
                            except:
                                city = '<MISSING>'
                                state = '<MISSING>'
                                zc = '<MISSING>'
                        country = csz.rsplit(',',1)[1].strip()
                        website = 'subway.co.uk'
                        hours = ''
                        typ = 'Restaurant'
                        store = item.split('locatorRestaurantNum\\">Restaurant #')[1].split('<')[0].strip()
                        name = 'Subway #' + store
                        phone = item.split('<div class=\\"locatorPhone\\">')[1].split('<')[0]
                        loc = '<MISSING>'
                        for sitem in ll:
                            if sitem.split('|')[0] == store:
                                lat = sitem.split('|')[1]
                                lng = sitem.split('|')[2]
                        days = item.split('<div class=\\"dayName\\">')
                        for day in days:
                            if '<div class=\\"openTime\\">' in day:
                                hrs = day.split('<')[0] + ': ' + day.split('<div class=\\"openTime\\">')[1].split('<')[0] + '-' + day.split('class=\\"closeTime\\">')[1].split('<')[0]
                                if hours == '':
                                    hours = hrs
                                else:
                                    hours = hours + '; ' + hrs
                        if store not in ids and state != '<MISSING>':
                            ids.append(store)
                            if '0' not in hours:
                                hours = '<MISSING>'
                            if phone == '':
                                phone = '<MISSING>'
                            if country == 'GBR':
                                country = 'GB'
                            yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
        logger.info("max count update")
        search.max_count_update(result_coords)
        coord = search.next_coord()

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
