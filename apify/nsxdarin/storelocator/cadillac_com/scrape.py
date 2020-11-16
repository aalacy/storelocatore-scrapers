import csv
from sgrequests import SgRequests
import json
from sglogging import SgLogSetup
from sgzip import sgzip

logger = SgLogSetup().get_logger('cadillac_com')

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
           'locale': 'en_US'
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
        try:
            x = coord[0]
            y = coord[1]
            url = 'https://www.cadillac.com/OCRestServices/dealer/latlong/v1/Cadillac/' + x + '/' + y + '/?distance=500&maxResults=500'
            logger.info('Pulling Lat-Long %s,%s...' % (str(x), str(y)))
            r = session.get(url, headers=headers)
            for line in r.iter_lines():
                line = str(line.decode('utf-8'))
                if '"id":' in line:
                    items = line.split('"id":')
                    for item in items:
                        if '"dealerName":"' in item:
                            name = item.split('"dealerName":"')[1].split('"')[0]
                            store = item.split(',')[0]
                            lat = item.split('"latitude":')[1].split(',')[0]
                            lng = item.split('"longitude":')[1].split('}')[0]
                            add = item.split('"addressLine1":"')[1].split('"')[0]
                            if 'addressLine2' in item:
                                add = add + ' ' + item.split('"addressLine2":"')[1].split('"')[0]
                            city = item.split('"cityName":"')[1].split('"')[0]
                            zc = item.split('"postalCode":"')[1].split('"')[0]
                            state = item.split('"countrySubdivisionCode":"')[1].split('"')[0]
                            country = item.split('"countryIso":"')[1].split('"')[0]
                            phone = item.split('{"phone1":"')[1].split('"')[0]
                            typ = 'Dealer'
                            try:
                                purl = item.split('"dealerUrl":"')[1].split('"')[0]
                            except:
                                purl = '<MISSING>'
                            website = 'cadillac.com'
                            hours = ''
                            if '"generalOpeningHour":[' in item:
                                hrs = item.split('"generalOpeningHour":[')[1].split('}],"serviceOpeningHour"')[0]
                                days = hrs.split('"openFrom":"')
                                for day in days:
                                    if '"openTo":"' in day:
                                        if hours == '':
                                            hours = day.split('"dayOfWeek":[')[1].split(']')[0].replace('1','Mon').replace('2','Tue').replace('3','Wed').replace('4','Thu').replace('5','Fri').replace('6','Sat').replace('7','Sun') + ': ' + day.split('"')[0] + '-' + day.split('"openTo":"')[1].split('"')[0]
                                        else:
                                            hours = hours + '; ' + day.split('"dayOfWeek":[')[1].split(']')[0].replace('1','Mon').replace('2','Tue').replace('3','Wed').replace('4','Thu').replace('5','Fri').replace('6','Sat').replace('7','Sun') + ': ' + day.split('"')[0] + '-' + day.split('"openTo":"')[1].split('"')[0]
                            else:
                                hours = '<MISSING>'
                            if len(zc) == 9:
                                zc = zc[:5] + '-' + zc[-4:]
                            if store not in ids:
                                ids.append(store)
                                logger.info('Pulling Store ID #%s...' % store)
                                yield [website, purl, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
        except:
            pass

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
