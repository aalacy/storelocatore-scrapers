from bs4 import BeautifulSoup
import csv
import string
import re, time

from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('goldendelirestaurant_com')



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
    
    url = 'https://www.thegoldendeli.com/contacts/'    
    r = session.get(url, headers=headers, verify=False)    
    soup =BeautifulSoup(r.text, "html.parser")    
   
    divlist = soup.findAll('div', {'class': 'contact-icon'})
   # logger.info("states = ",len(state_list))
    p = 0
    cleanr = re.compile(r'<[^>]+>')
    for div in divlist:
        det = div.findAll('p')
        det =det[1]
        det = re.sub(cleanr,' ',str(det)).splitlines()
        street = det[0]
        city, state = det[1].split(', ',1)
        state = state.lstrip()
        state,pcode= state.split(' ',1)
        phone = det[2]
        hourlist = div.find('ul',{'class':'list'}).findAll('li')
        hours = ''
        for hr in hourlist:
            hours = hours + hr.text + ' '
        if len(hours) < 2:
            hour = '<MISSING>'
        lat = '<MISSING>'
        longt  = '<MISSING>'
        '''if p == 0:
            lat = str(soup).split('"lat":')[1].split(',',1)[0]
            lat = lat[0:9]           
            longt = str(soup).split('"lng":')[1].split(',',1)[0]
            longt = longt[0:9]    '''
        data.append(['https://goldendelirestaurant.com/',url,city,street,city,state,pcode,'US',
                        '<MISSING>',
                        phone,
                       '<MISSING>',
                        '<MISSING>',
                        '<MISSING>',
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
