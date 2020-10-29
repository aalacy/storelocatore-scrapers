from bs4 import BeautifulSoup
import csv
import string
import re, time

from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('beansandbrews_com')



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
    p = 0
    url = 'https://www.beansandbrews.com/locations/'    
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text,'html.parser')    
      
    divlist = soup.findAll('a', {'class': 'location'})
    logger.info("states = ",len(divlist))
    for div in divlist:
        link = div['href']
        #logger.info(link)
        r = session.get(link, headers=headers, verify=False)
        soup = BeautifulSoup(r.text,'html.parser')
        title = soup.find('h4').text
        address = soup.findAll('p')[0].text.splitlines()
        street = address[0]
        i = 1
        while True:
            try:
                city,state = address[i].split(', ')
                i += 1
                break
            except:
                street = street +' '+address[i]
                i += 1
               
      
        state,pcode = state.lstrip().split(' ',1)        
        phone = soup.findAll('p')[1].text
        hours =  soup.findAll('p')[2].text.replace('\n', ' ').replace('\r','')       
        data.append([
                        'https://www.beansandbrews.com/',
                        link,                   
                        title,
                        street,
                        city,
                        state,
                        pcode,
                        'US',
                        '<MISSING>',
                        phone.replace('Phone:','').lstrip(),
                        '<MISSING>',
                        '<MISSING>',
                        '<MISSING>',
                        hours.replace('\r','').replace('\n','').replace('Hours:','').lstrip()
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
