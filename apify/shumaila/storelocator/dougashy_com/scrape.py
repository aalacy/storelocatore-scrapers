import requests
from bs4 import BeautifulSoup
import csv
import string
import re, time
import usaddress
import json
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('dougashy_com')



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
    
    url = 'https://dougashy.com/locations/'
    r = session.get(url, headers=headers, verify=False)    
    soup =BeautifulSoup(r.text, "html.parser")
    #divlist = soup.findAll('div',{'class':'fl-rich-text'})
    linklist = soup.find('ul',{'class':'sub-menu'}).findAll('li')
    logger.info(len(linklist))  
    det = r.text.split('var wpgmaps_localize_marker_data = ')[1].split('var wpgmaps_localize_global_settings =')[0]
    det = re.sub(r'"[1-9]":', "", det)
    det = '['+det.replace(';',']').replace('}]',']')
    det = det.replace('[{','[')   
    coordlist = json.loads(det)        
    p = 0
    #for div in divlist:
    for link in linklist:
        link = link.find('a')['href']
        #logger.info(link)
        r = session.get(link, headers=headers, verify=False)
        soup =BeautifulSoup(r.text, "html.parser")
        divlist = soup.findAll('div',{'class':'fl-rich-text'})
        for div in divlist:
            if div.text.find('Address') > -1:
                title = div.find('h2').text
                det = div.findAll('p')
                address = det[0].text.splitlines()
                street = address[1]
                state = address[2].replace(', , ',', ')
                #logger.info(state)
                city,state = state.split(', ',1)
                state = state.lstrip()
                #logger.info(state)
                state,pcode = state.split(' ')
                phone = div.find('a').text
                for mp in det:
                    if mp.text.find('Hours') > -1:
                        hours = mp.text.replace('\n', ' ').replace('Store Hours','').lstrip()

                lat = '<MISSING>'
                longt = '<MISSING>'
                for coord in coordlist:                
                    if coord['address'].replace(',','').replace('.','').find(street.replace(',','').replace('.','')) > -1:
                        lat = coord['lat']
                        longt = coord['lng']
                data.append([
                            'https://dougashy.com/',
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
                #input()
            
    return data


def scrape():
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))

scrape()
