from bs4 import BeautifulSoup
import csv
import string
import re, time

from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('sesameplace_com')



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
    cleanr = re.compile(r'<[^>]+>')
    url = 'https://sesameplace.com/'
    r = session.get(url, headers=headers, verify=False)   
    soup =BeautifulSoup(r.text, "html.parser")
    linklist = soup.select('a:contains("Visit")')
    for link in linklist:
        logger.info(link['href'])
        title = link.text.split('in ',1)[1]
        link = link['href']
        r = session.get(link, headers=headers, verify=False)
        address = r.text.split('All Rights Reserved. ',1)[1].split('<',1)[0]
        street,city,state = address.split(', ')
        state,pcode = state.lstrip().split(' ',1)
        try:
            phone = r.text.split('tel:',1)[1].split('"')[0]
        except:
            phone = '<MISSING>'
        try:
            lat = r.text.split('"ParkCenterpointLatitude":',1)[1].split(',',1)[0]
        except:
            lat = '<MISSING>'
        try:
            longt = r.text.split('"ParkCenterpointLongitude":',1)[1].split(',',1)[0]
            
        except:
            longt = '<MISSING>'
        
        data.append([
                        'https://sesameplace.com/',
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
                        '<INACCESSIBLE>'
                    ])
        #logger.info(p,data[p])
        p += 1
                
            
    
        
    return data


def scrape():    
    data = fetch_data()
    write_output(data)
   

scrape()
