from bs4 import BeautifulSoup
import csv
import string
import re, time
import json

from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('greatsouthernbank_com')



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
    url = 'https://www.greatsouthernbank.com/_/api/branches/37.2075589/-93.2605231/25'
    r = session.get(url, headers=headers, verify=False)
    r = r.text.split('"branches":')[1].split(']}')[0]+']'
    locations =json.loads(r)
    #logger.info(len(locations))
    for loc in locations:
        title = loc['name']
        store = loc['id']
        lat = loc['lat']
        longt = loc['long']
        street = loc['address']
        city = loc['city']
        state = loc['state']
        pcode = loc['zip']
        phone = loc['phone']
        detail = loc['description']
        detail = BeautifulSoup(detail,'html.parser')
        try:
            link = detail.find('a')['href']
            #logger.info(link)
            r = session.get(link, headers=headers, verify=False)
            soup = BeautifulSoup(r.text,'html.parser')
            hourd =soup.find('table',{'class':'hours'})
            hourd = hourd.findAll('tr')
            
            hours = ''
            for hr in hourd:
                hours = hours + hr.text + ' '
               

        
            if len(hours) <3:
                hours = '<MISSING>'
            else:
                hours = hours.replace('Day of the WeekHours','').replace('day','day ')
                
        except:
            
                
            link = '<MISSING>'
            hours = detail.find('li').text
                
        data.append([
                'https://greatsouthernbank.com',
                link,                   
                title,
                street,
                city,
                state,
                pcode,
                'US',
                store,
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
