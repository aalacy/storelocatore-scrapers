
import requests
from bs4 import BeautifulSoup
import csv
import string
import re, time

from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('haloburger_com')



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
    cleanr = re.compile(r'<[^>]+>')    
    url = 'https://haloburger.com/stores-sitemap.xml'    
    r = session.get(url, headers=headers, verify=False)
    soup =BeautifulSoup(r.text, "html.parser")   
    link_list = soup.findAll('loc')
    #logger.info("states = ",len(link_list))
    p = 0
    for link in link_list:
        link = link.text      
        r = session.get(link, headers=headers, verify=False)        
        soup = BeautifulSoup(r.text, "html.parser")
        title = soup.find('h2',{'itemprop':'name'}).text.replace('\n','').lstrip()
        address = soup.find('div',{'class':'store_locator_single_address'})
        address = cleanr.sub('\n', str(address)).splitlines()        
        street = address[3]
        #logger.info(address)
        city, state = address[4].split(', ',1)
        state = state.lstrip()
        state , pcode = state.split(' ',1)
        if len(pcode) < 2:
            pcode = '<MISSING>'
        try:
            phone = soup.find('div',{'class':'store_locator_single_contact'}).find('a').text
        except:
            phone = '<MISSING>'
        try:
            hourlist = soup.find('div',{'class':'store_locator_single_opening_hours'})
            hourlist = cleanr.sub('\n', str(hourlist)).splitlines()
            hours = ''
            for i in range(1,len(hourlist)):
                hours = hours + hourlist[i] + ' '
            if len(hours) < 3:
                hours = '<MISSING>'
            else:
                hours = hours.replace('Opening Hours','').lstrip().rstrip()
                
        except:
            hours = '<MISSING>'
            
        try:
            coords = soup.find('div',{'class':'store_locator_single_map'})
            lat = coords['data-lat']
            longt = coords['data-lng']
        except:
            lat = '<MISSING>'
            longt = '<MISSING>'
            
        data.append([
            'https://haloburger.com/',
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
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))

scrape()
