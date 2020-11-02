import csv
from sgrequests import SgRequests
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('scs_co_uk')



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
    locs = []
    x = 0
    y = 0
    url = 'https://www.scs.co.uk/on/demandware.store/Sites-SFRA_SCS-Site/en_GB/Stores-FindStores?showMap=true&radius=1000.0&lat=' + str(x) + '&long=' + str(y) + '&storeCount=5&searchKey='
    r = session.get(url, headers=headers)
    for item in json.loads(r.content)['stores']:
        name = item['name']
        website = 'scs.co.uk'
        try:
            add = item['address1'] + ' ' + item['address2']
        except:
            add = item['address1']
        add = add.strip()
        city = item['city']
        try:
            state = item['stateCode']
        except:
            state = '<MISSING>'
        zc = item['postalCode']
        lat = item['latitude']
        lng = item['longitude']
        phone = item['phone']
        country = item['countryCode']
        store = item['ID']
        typ = '<MISSING>'
        purl = 'https://www.scs.co.uk/stores/' + item['storeTag']
        hours = ''
        hrinfo = item['openingHoursTable']
        hrinfo = hrinfo.replace('\\r','').replace('\\n','').replace('\r','').replace('\n','')
        days = hrinfo.split('<td class=\"day\">')
        for day in days:
            if 'b-store-hours' not in day:
                hrs = day.split('<')[0] + ': ' + day.split('class=\"hour\">')[1].split('<')[0]
                if hours == '':
                    hours = hrs
                else:
                    hours = hours + '; ' + hrs
        phone = phone.replace('"',"'")
        lat = '51.6570083'
        lng = '-3.9030564'
        if 'tel:' in phone:
            phone = phone.split("tel:")[1].split("'")[0]
        if add not in locs:
            locs.append(add)
            yield [website, purl, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

    for x in range(50, 59):
        for y in range(-8, 1):
            logger.info('%s-%s...' % (str(x), str(y)))
            url = 'https://www.scs.co.uk/on/demandware.store/Sites-SFRA_SCS-Site/en_GB/Stores-FindStores?showMap=true&radius=1000.0&lat=' + str(x) + '&long=' + str(y) + '&storeCount=5&searchKey='
            r = session.get(url, headers=headers)
            for item in json.loads(r.content)['stores']:
                name = item['name']
                website = 'scs.co.uk'
                try:
                    add = item['address1'] + ' ' + item['address2']
                except:
                    add = item['address1']
                add = add.strip()
                city = item['city']
                try:
                    state = item['stateCode']
                except:
                    state = '<MISSING>'
                zc = item['postalCode']
                lat = item['latitude']
                lng = item['longitude']
                phone = item['phone']
                country = item['countryCode']
                store = item['ID']
                typ = '<MISSING>'
                purl = 'https://www.scs.co.uk/stores/' + item['storeTag']
                hours = ''
                hrinfo = item['openingHoursTable']
                hrinfo = hrinfo.replace('\\r','').replace('\\n','').replace('\r','').replace('\n','')
                days = hrinfo.split('<td class=\"day\">')
                for day in days:
                    if 'b-store-hours' not in day:
                        hrs = day.split('<')[0] + ': ' + day.split('class=\"hour\">')[1].split('<')[0]
                        if hours == '':
                            hours = hrs
                        else:
                            hours = hours + '; ' + hrs
                phone = phone.replace('"',"'")
                if 'tel:' in phone:
                    phone = phone.split("tel:")[1].split("'")[0]
                if '0' not in phone and '1' not in phone:
                    phone = '<MISSING>'
                if add not in locs:
                    locs.append(add)
                    yield [website, purl, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
