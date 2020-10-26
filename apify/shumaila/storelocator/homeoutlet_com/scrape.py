from bs4 import BeautifulSoup
import csv
import string
import re, time

from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('homeoutlet_com')



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
    p = 0
    data = []
    pattern = re.compile(r'\s\s+')
    cleanr = re.compile(r'<[^>]+>')
    page = 0
    while True:
        url = 'https://www.homeoutlet.com/store-locator?page='+str(page)
        r = session.get(url, headers=headers, verify=False)
        
        soup =BeautifulSoup(r.text, "html.parser")
       
        divlist = soup.findAll('div', {'class': "store-card"})
        if len(divlist) == 0:
            break
        for div in divlist:
            title = div.find('div',{'class':'field-name'}).text.strip()
            street = div.find('span',{'class':'address-line1'}).text
            city = div.find('span',{'class':'locality'}).text
            state = div.find('span',{'class':'administrative-area'}).text
            pcode = div.find('span',{'class':'postal-code'}).text
            phone = div.find('div',{'class':'field-phone'}).text
            hours = div.find('div',{'class':'store-hours'}).text
            link = div.find('div',{'class':'choose-store'}).findAll('a')[1]['href']
            #logger.info(link)
            r = session.get(link, headers=headers, verify=False)
            try:
                lat = r.text.split('"latitude": "',1)[1].split('"',1)[0]
                longt = r.text.split('"longitude": "',1)[1].split('"',1)[0]
            except:
                lat = longt = '<MISSING>'
            hours = re.sub(pattern,' ',hours).replace('Store Hours*','').strip()
            try:
                hours  = hours.split('*',1)[0]
            except:
                pass
            
            data.append([
                        'https://www.homeoutlet.com/',
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
            
                

        page = page + 1
        
    return data


def scrape():
    
    data = fetch_data()
    write_output(data)
    
scrape()
