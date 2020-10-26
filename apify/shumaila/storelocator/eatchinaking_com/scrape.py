from bs4 import BeautifulSoup
import csv
import string
import re, time
import json
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('eatchinaking_com')



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
    url = 'http://eatchinaking.com/locations/'
    p = 0
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text,'html.parser')
    table = soup.find('table',{'id':'tablepress-2'}).find('tbody').findAll('tr')
    for row in table:

        
        cols = row.findAll('td')
        title = cols[0].text
        street = cols[1].text
        pcode = cols[2].text
        state = cols[3].text
        city = cols[0].text
        phone = cols[4].text
        if len(phone) < 3:
            phone = '<MISSING>'
        data.append([
                'http://eatchinaking.com/',
                'http://eatchinaking.com/locations/',                   
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
                '<MISSING>'
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

