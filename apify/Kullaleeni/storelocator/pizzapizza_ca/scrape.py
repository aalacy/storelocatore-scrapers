from bs4 import BeautifulSoup
import csv
import string
import re, time

from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('pizzapizza_ca')


session2 = SgRequests()
session1 = SgRequests()
session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
           'x-request-id': 'bd65600d-8669-4903-8a14-af88203add38',
            'session-token': '5e57f395-4453-44a4-9b02-8c73904b1168'
           }
headers1 = {'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36',
           'x-request-id': '449704b9-6540-48b0-b9f2-432fa5dd1891',
            'session-token': '029149bd-86ba-4246-9d90-c6e3eb5ea850'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    # Your scraper here
    data = []
    p = 0
    url = 'https://www.pizzapizza.ca/ajax/store/api/v1/province_cities'
    r = session.get(url, headers=headers, verify=False).json()
    logger.info(r)
    for states in r:
        province = states['province_slug']
        # logger.info(province)
        cities = states['cities']
        for city in cities:
            # logger.info(city['city_slug'])
            mlink = 'https://www.pizzapizza.ca/restaurant-locator/'+province + '/'+city['city_slug']
            branchlink = 'https://www.pizzapizza.ca/ajax/store/api/v1/search/store_locator?province='+province+'&city='+city['city_slug']
            # logger.info(branchlink)
            try:
                r1 = session.get(branchlink, headers=headers, verify=False).json()
                r = r1['stores']
            except:
                try:
                    # logger.info("Next session use")
                    r1 = session1.get(branchlink, headers=headers1, verify=False).json()
                    r = r1['stores']
                except:
                    # logger.info("Final session use")
                    r1 = session2.get(branchlink, headers=headers, verify=False).json()
                    r = r1['stores']
            for branch in r:
                # logger.info(branch)
                title = branch['name']
                street = branch['address'].lstrip()
                city = branch['city']
                state = branch['province']
                pcode = branch['postal_code']
                store = str(branch['store_id'])
                hourlist = branch['operating_hours']
                phone = branch['market_phone_number']
                lat = branch['latitude']
                longt = branch['longitude']
                hours = ''
                for hr in hourlist:
                    hours = hours + hr['label'] + ' '+ hr['start_time']+' : ' +hr['end_time'] +' '
                link = mlink + '/'+ street.lstrip().lower().replace(' ','-')+'/'+store
                data.append([
                        'https://www.pizzapizza.ca/',
                        link,
                        title,
                        street,
                        city,
                        state,
                        pcode,
                        'CA',
                        store,
                        phone,
                        '<MISSING>',
                        lat,
                        longt,
                        hours
                    ])
                #logger.info(p,data[p])
                p += 1
        
    return data


def scrape():
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))

scrape()
