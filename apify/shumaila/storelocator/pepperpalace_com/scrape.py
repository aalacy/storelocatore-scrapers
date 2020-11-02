from bs4 import BeautifulSoup
import csv
import string
import re, time
import json
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('pepperpalace_com')



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
   
    data = []
    cleanr = re.compile(r'<[^>]+>')    
    url = 'https://stockist.co/api/v1/u5383/locations/all.js?callback=_stockistAllStoresCallback'
    p = 0
    r = session.get(url, headers=headers, verify=False)
    r = r.text.split('_stockistAllStoresCallback(')[1].split(');')[0]
    loclist = json.loads(r)
    for loc in loclist:
        #logger.info(loc)
        title = loc['name']
        store = loc['id']
        lat = loc['latitude']
        longt = loc['longitude']
        street = loc['address_line_1']
        city = loc['city']
        state = loc['state']
        pcode = loc['postal_code']
        try:
            ccode = loc['country']
            if ccode.find('Canada') > -1:
                ccode = 'CA'
            elif ccode.find('States') > -1:
                ccode = 'US'
        except:
            ccode = 'US'
        
        phone = loc['phone']
        if state.find('Wisconsin') > -1:
            state = 'WI'
        if pcode.find('L9Y OV2') > -1 and ccode == 'CA':
            pcode = pcode.replace('O','0')
        if title.find('Coming Soon') == -1:
            data.append([
                'https://pepperpalace.com/',
                'https://pepperpalace.com/pages/store-locator',                   
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
                '<MISSING>'
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

