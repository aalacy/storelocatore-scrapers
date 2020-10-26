from bs4 import BeautifulSoup
import csv
import string
import re, time

from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('kayndaves_com')



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
    url = 'https://www.kayndaves.com/'
    r = session.get(url, headers=headers, verify=False)    
    soup =BeautifulSoup(r.text, "html.parser")
   
    divlist = soup.find('div', {'id': "comp-kczp38o9"}).findAll('div',{'data-testid':'richTextElement'})
    
   # logger.info("states = ",len(state_list))
    p = 0
    for div in divlist:
        content = div.text.strip().splitlines()
        title = content[0]
        street = div.findAll('a')[0].text
        phone = div.findAll('a')[1].text.strip()
        hours = content[4]        
        lat,longt = div.find('a')['href'].split('@',1)[1].split('data',1)[0].split(',',1)
        longt = longt.split(',',1)[0]
        data.append([
                        'https://www.kayndaves.com/',
                        'https://www.kayndaves.com/',                   
                        title,
                        street,
                        title,
                        'CA',
                        '<MISSING>',
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
   
    data = fetch_data()
    write_output(data)
  

scrape()
