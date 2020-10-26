from bs4 import BeautifulSoup
import csv
import string
import re, time
import json
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('jimmyjazz_com')



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
    pattern = re.compile(r'\s\s+') 
    cleanr = re.compile(r'<[^>]+>')    
    url = 'https://cdn.shopify.com/s/files/1/0267/9232/9325/t/21/assets/sca.storelocatordata.json?v=1591108884&formattedAddress=&boundsNorthEast=&boundsSouthWest='
    p = 0
    loclist = session.get(url, headers=headers, verify=False).json()
    
    for loc in loclist:
        title = loc['name']
        try:
            title = title + ' ' +loc['description']
        except:
            pass
        store = loc['id']
        lat = loc['lat']
        longt = loc['lng']
        street = loc['address']
        city = loc['city']
        state = loc['state']
        pcode = loc['postal']        
        try:
            hours = loc['schedule']
        except:
            hours = '<MISSING>'
        
       
        phone = loc['phone']
        if phone == 'TBA':
            phone = '<MISSING>'
        if len(pcode) == 4:
            pcode = '0' + pcode
        if state.find('Wisconsin') > -1:
            state = 'WI'
        
        if title.find('Coming Soon') == -1:
            data.append([
                'https://www.jimmyjazz.com/',
                'https://www.jimmyjazz.com/pages/store-locator',                   
                title,
                re.sub(pattern,'',street),
                re.sub(pattern,'',city),
                state,
                pcode,
                'US',
                store,
                phone,
                '<MISSING>',
                lat,
                longt,
                hours.replace('\n',' ').replace('Ð ','-').replace('<br>',' ').replace('\\r\\n',' ')
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

