import requests
from bs4 import BeautifulSoup
import csv
import string
import re, time
import json
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('yoshinoyaamerica_com')



session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
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
    cleanr = re.compile(r'<[^>]+>')    
    url = 'https://www.yoshinoyaamerica.com/location/viewer/searchdb.php?lat=37.5952304&lng=-122.043969&value=10000&r=0.4061677943961699'
    
    p = 0
    r = session.get(url, headers=headers, verify=False)
    #r = r.text.split('_stockistAllStoresCallback(')[1].split(');')[0]
    loclist = json.loads(r.text)
    for loc in loclist:
        title = loc['n']
        store = '<MISSING>'
        lat = loc['lat']
        longt = loc['lng']
        street = loc['a']
        try:
            street, city = street.split(', ')
            #street = street.split(', ')[0]
        except:
            city = '<MISSING>'
        state = loc['s']
        pcode = loc['pc']
        ccode = 'US'
        try:
            phone = loc['p']
        except:
            phone = '<MISSING>'
        try:
            hours = loc['m1']
        except:
            hours = '<MISSING>'
        if title.find('Coming Soon') == -1:
            data.append([
                'https://www.yoshinoyaamerica.com/',
                'https://yoshinoyaamerica.com/locations',                   
                title,
                street,
                city,
                state,
                pcode,
                ccode,
                store,
                phone,
                '<MISSING>',
                lat,
                longt,
                hours
            ])
            #logger.info(p,data[p])
            p += 1
            #input()
        


    
                
        
    return data


def scrape():
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))

scrape()

