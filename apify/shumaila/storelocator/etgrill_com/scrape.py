from bs4 import BeautifulSoup
import csv
import string
import re, time

from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('etgrill_com')



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
    pattern = re.compile(r'\s\s+') 
    url = 'https://www.etgrill.com/contact/brea/'
    r = session.get(url, headers=headers, verify=False)  
    soup =BeautifulSoup(r.text, "html.parser")
    mainul = soup.find('ul',{'id':'menu-contact-menu'})
    linklist = mainul.findAll('a')
    for link in linklist:
        title =link.text
        link = link['href']
        if link == r.url:
            pass
        else:
            r = session.get(link, headers=headers, verify=False)
            soup =BeautifulSoup(r.text, "html.parser")

        section = soup.find('section',{'class':'page__content'}).text
        section = re.sub(pattern,' ',section)
        det = section.split('Address & Phone')[1].split('HOURS')[0]        
        det = det.splitlines()
        street = det[1]
        city,state = det[2].split(', ',1)
        state,pcode = state.lstrip().split(' ',1)
        phone  = det[3]
        hours = section.split('HOURS')[1].split('SUNDAY BRUNCH')[0].replace('\n',' ')
        coord = soup.find('div',{'class':'gmap'})['data-url']
        coord = coord.split('@')[1].split('/data')[0]
        lat,longt = coord.split(',',1)
        longt = longt.split(',',1)[0]
        data.append([
                        'https://www.etgrill.com/',
                        link,                   
                        title,
                        street,
                        title,
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
