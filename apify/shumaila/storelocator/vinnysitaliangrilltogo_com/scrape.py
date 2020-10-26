from bs4 import BeautifulSoup
import csv
import string
import re, time

from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('vinnysitaliangrilltogo_com')



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
    pattern = re.compile(r'\s\s+')
    cleanr = re.compile(r'<[^>]+>')
    url = 'https://vinnysitaliangrilltogo.com'
    r = session.get(url, headers=headers, verify=False)
    soup =BeautifulSoup(r.text, "html.parser")
   
    divlist = soup.findAll('div', {'class': "footer-address-loc"})
   # logger.info("states = ",len(state_list))
    p = 0
    for div in divlist:
        content = div.text.lstrip().rstrip().splitlines()
        title = content[0]
        street,city,state = content[1].lstrip().split(', ',2)
        state,pcode = state.lstrip().split(' ',1)
        pcode  = pcode.lstrip().split(',')[0]
        phone = content[2]
        hours = ' '.join(content[3:])
        data.append([
                        'https://vinnysitaliangrilltogo.com',
                        'https://vinnysitaliangrilltogo.com',                   
                        title,
                        street,
                        city,
                        state,
                        pcode,
                        'US',
                        '<MISSING>',
                        phone.replace('Phone: ',''),
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
