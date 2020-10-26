from bs4 import BeautifulSoup
import csv
import string
import re, time

from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('healthworksfitness_com')



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
    
    url = 'https://healthworksfitness.com/our-locations/'
    r = session.get(url, headers=headers, verify=False)  
    soup =BeautifulSoup(r.text, "html.parser")   
    linklist = soup.find('li',{'id':'menu-item-11140'}).find('ul').findAll('li')
    #logger.info("states = ",len(linklist))    
    p = 0
    for link in linklist:
        link = link.find('a')
        #logger.info(link.text)
        if link.text.lower().find('about') > -1 or link.text.lower().find('community') > -1:
            pass
        else:
            title = link.text
            link = link['href']
            
            #logger.info(link)
            r = session.get(link, headers=headers, verify=False)  
            soup =BeautifulSoup(r.text, "html.parser")
            hours = ''
            address = '' 
            det = soup.findAll('p')
            for div in det:
                if div.text.find('Address') > -1:
                    address = div.text
                
                elif div.text.find('AM') > -1 and div.text.find('PM') > -1:
                    hours = div.text
                    #logger.info(hours)
            if hours != '':
                hours = hours.replace('\n',' ').replace('\xa0','').replace('Club Hours ','').lstrip()
            else:
                hours = '<MISSING>'
            #logger.info(hours)
            coord = soup.find('div',{'class':'map-marker'})
            #logger.info(address)
            if address != '':
                address= address.splitlines()
                phone = address[0]
                #logger.info(address[1])
                adr = address[1].split('Address:',1)[1].lstrip()
                street,city,state = adr.split(', ')
                state,pcode = state.lstrip().split(' ')
                lat = coord['data-lat']
                longt = coord['data-lng']
                data.append([
                        'https://healthworksfitness.com/',
                        link,                   
                        title,
                        street,
                        city,
                        state,
                        pcode,
                        'US',
                        '<MISSING>',
                        phone.replace('Telephone:\xa0',''),
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
