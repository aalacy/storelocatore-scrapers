from bs4 import BeautifulSoup
import csv
import string
import re, time, usaddress

from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('raleys_com__something-extra__pump-rewards__aisle-1-locations')



session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36'
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
    url = 'https://www.raleys.com/something-extra/pump-rewards/aisle-1-locations/'
    r = session.get(url, headers=headers, verify=False)
    
    soup =BeautifulSoup(r.text, "html.parser")
    divlist = soup.find('div',{'class':'entry-content'}).findAll('div', {'class': "col-sm-4"})
    #logger.info(len(divlist))    
    p = 0
    for div in divlist:
        try:
            title = div.find('h3').text
        except:
            continue
        address = div.find('address').text
        coord = div.find('a')['href']
        r = session.get(coord, headers=headers, verify=False)
        lat,longt = r.url.split('@',1)[1].split('data',1)[0].split(',',1)
        longt = longt.split(',',1)[0]
        address = usaddress.parse(address)
        i = 0
        street = ""
        city = ""
        state = ""
        pcode = ""
        while i < len(address):
            temp = address[i]
            if temp[1].find("Address") != -1 or temp[1].find("Street") != -1 or temp[1].find('Occupancy') != -1 or temp[1].find("Recipient") != -1 or temp[1].find("BuildingName") != -1 or temp[1].find("USPSBoxType") != -1 or temp[1].find("USPSBoxID") != -1:
                street = street + " " + temp[0]
            if temp[1].find("PlaceName") != -1:
                city = city + " " + temp[0]
            if temp[1].find("StateName") != -1:
                state = state + " " + temp[0]
            if temp[1].find("ZipCode") != -1:
                pcode = pcode + " " + temp[0]
            i += 1

        street = street.lstrip().replace(',','')
        city = city.lstrip().replace(',','')
        state = state.lstrip().replace(',','')
        pcode = pcode.lstrip().replace(',','')
        
        data.append([
                        'https://raleys.com/something-extra/pump-rewards/aisle-1-locations',
                        'https://raleys.com/something-extra/pump-rewards/aisle-1-locations',                   
                        title,
                        street.replace('\n',''),
                        city,
                        state,
                        pcode,
                        'US',
                        '<MISSING>',
                        '<MISSING>',
                        '<MISSING>',
                        lat,
                        longt,
                        '<MISSING>'
                    ])
        #logger.info(p,data[p])
        p += 1
                
            
     
           
        
    return data


def scrape():
    
    data = fetch_data()
    write_output(data)
    

scrape()
