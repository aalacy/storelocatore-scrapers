from bs4 import BeautifulSoup
import csv
import string
import re, time

from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('nofrillssupermarkets_com')



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
    url = 'https://nofrillssupermarkets.com/'
    r = session.get(url, headers=headers, verify=False)   
    soup =BeautifulSoup(r.text, "html.parser")
   
    divlist = soup.find('ul', {'id': "avia-menu"}).findAll('li')[2].find('ul').findAll('a')
    #logger.info(len(divlist))
    p = 0
    for div in divlist:
        title = div.text
        link = 'https://nofrillssupermarkets.com/'+div.text.lower().replace(' ','-')
        #link = div.find('a',{'itemprop':'url'})#['href']
        #logger.info(link)
        r = session.get(link, headers=headers, verify=False)
        soup = BeautifulSoup(r.text,'html.parser')
        content = soup.find('section',{'class':'av_textblock_section'}).text.splitlines()
        street = content[1]
        city, state = content[2].split(', ')
        state,pcode = state.lstrip().split(' ')
        phone = content[4]
        hours = ' '.join(content[6:])
        longt,lat = soup.find('iframe')['src'].split('!2d',1)[1].split('!2m',1)[0].split('!3d',1)
        
        data.append([
                        ':https://nofrillssupermarkets.com/',
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
                
            
       
           
        
    return data


def scrape():   
    data = fetch_data()
    write_output(data)
   

scrape()
