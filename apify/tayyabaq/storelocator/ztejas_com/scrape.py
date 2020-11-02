from bs4 import BeautifulSoup
import csv
import string
import re, time

from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('ztejas_com')



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
    
    url = 'https://ztejas.com/location.html'
    r = session.get(url, headers=headers, verify=False)
  
    soup =BeautifulSoup(r.text, "html.parser")
   
    divlist = soup.findAll('div', {'class': 'locations-details'})
   # logger.info("states = ",len(state_list))
    p = 0
    for div in divlist:
        title = div.find('h5').text
        try:
            coord = div.find('iframe')['src']
            longt,lat = coord.split('!2d',1)[1].split('!3m',1)[0].split('!3d')
        except:
            lat = '<MISSING>'
            longt = '<MISSING>'
        div = div.findAll('p')
        
        hours = div[0].text
        phone = div[1].text
        address = div[2].text
        #logger.info(address)
        temp = address.split(', ')
        state = temp[-1]
        street =address.replace(', '+state,'')
        #logger.info(street)
        state,pcode = state.lstrip().split(' ',1)
        city = street.split(' ')[-1]
        street = street.replace(' '+city,'')
        data.append([
                        'https://ztejas.com',
                        'https://ztejas.com/location.html',                   
                        title,
                        street,
                        city,
                        state,
                        pcode,
                        'US',
                        '<MISSING>',
                        phone.replace('Phone: ',''),
                        '<MISSING>',
                        lat,
                        longt,
                        hours.replace('Hours:  ','')
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
