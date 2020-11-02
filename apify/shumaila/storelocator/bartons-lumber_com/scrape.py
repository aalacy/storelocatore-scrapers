from bs4 import BeautifulSoup
import csv
import string
import re, time

from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('bartons-lumber_com')



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
    url = 'https://www.bartons-lumber.com/'
    r = session.get(url, headers=headers, verify=False)
    
    soup =BeautifulSoup(r.text, "html.parser")
   
    divlist = soup.select_one('li:contains("Locations")').select("a[href*=content]")
    
   # logger.info("states = ",len(state_list))
    p = 0
    for div in divlist:
        link = 'https://www.bartons-lumber.com' + div['href']
        #logger.info(link)
        r = session.get(link, headers=headers, verify=False)
        soup =BeautifulSoup(r.text, "html.parser")
        title  = soup.find('h1').text
        street = soup.find('div',{'class':'street-block'}).text
        city = soup.find('span',{'class':'locality'}).text
        state = soup.find('span',{'class':'state'}).text
        pcode = soup.find('span',{'class':'postal-code'}).text
        phone = soup.find('div',{'class':'field-name-gsl-props-phone'}).text
        hours = soup.find('section',{'class':'field-type-office-hours'}).text
        hourlist = soup.findAll('span',{'class':'oh-display'})
        hours = ''
        for hr in hourlist:
            hours = hours + hr.text +' '
       
        data.append([
                        'https://www.bartons-lumber.com/',
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
                        '<MISSING>',
                        '<MISSING>',
                        hours
                    ])
        #logger.info(p,data[p])
        p += 1
        
        
    return data


def scrape():
  
    data = fetch_data()
    write_output(data)
  

scrape()
