#rewritten by Shumaila Ali
from bs4 import BeautifulSoup
import csv
import string
import re, time, json

from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('giuseppezanotti_com')



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
    p = 0
    data = []
    pattern = re.compile(r'\s\s+') 
    url = 'https://www.giuseppezanotti.com/wo/amlocator/index/ajax/'
    loclist = session.get(url, headers=headers, verify=False).json()['items']
    for loc in loclist:
        if loc['country'] == 'US':
            #logger.info(loc)
            store = loc['id']
            title = loc['name']
            ccode = loc['country']
            city = loc['city']
            pcode = loc['zip']
            try:                
                state,pcode = pcode.lstrip().split(' ',1)
            except:
                try:                    
                    city,state = city.split(' ',1)
                except:
                    if city == 'Orlando':
                        state = 'FL'

            try:
                temp, state = state.split(', ')
                city = city + ' '+temp
            except:
                pass
            try:
                state,pcode = pcode.split(' ',1)               
            except:
                pass
            phone = loc['phone']
            lat = loc['lat']
            longt = loc['lng']
            street = loc['address']
            link = loc['url'].split('href="',1)[1].split('"')[0]
            hourlist = json.loads(loc['schedule_string'])
            hours = ''
            for hr in hourlist:
                day = hr
                sthr = hourlist[day]['from']['hours']
                stmin = hourlist[day]['from']['minutes']
                endhr = (int)(hourlist[day]['to']['hours'])
                if endhr > 12:
                    endhr = endhr-12
                endmin = hourlist[day]['to']['minutes']

                hours = hours + day +' '+ sthr + " : " + stmin + ' AM - ' + str(endhr) + " : " + endmin + ' PM  ' 
            
          
            data.append([
                        'https://www.giuseppezanotti.com/',
                        link,                   
                        title,
                        street,
                        city,
                        state,
                        pcode,
                        'US',
                        '<MISSING>',
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
