from bs4 import BeautifulSoup
import csv
import string
import re, time
import json
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('zizzi_co_uk')



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
    url = 'https://www.zizzi.co.uk/wp-json/locations/get_venues'
    p = 0
    loclist = session.get(url, headers=headers, verify=False).json()['data']
    
    for loc in loclist:

        #logger.info(loc['address'])
        title = loc['title']
        if title.find('Opening Soon') == -1:
            try:
                street,city,pcode = loc['address'].split("\r\n")
            except:
                street,temp,city,pcode = loc['address'].split("\r\n")
                street = street + ' '+ temp
                
            if len(pcode)<3:
                street,city,pcode = loc['address'].split("\r\n",2)
                pcode = pcode.replace("\r\n",'')
            
            if len(pcode)<3:
                pcode = '<MISSING>'
            
            store = loc['id']
            link = loc['link']
            lat = loc['latitude']
            longt = loc['longitude']
            phone = loc['phone_number']            
            state = loc['region']
            if lat.find('@') > -1:
                lat = '<MISSING>'
        
            data.append([
                'https://www.zizzi.co.uk/',
                link,                   
                title,
                street,
                city,
                state,
                pcode,
                'GB',
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

