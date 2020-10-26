import requests
from bs4 import BeautifulSoup
import csv
import string
import re, time
import usaddress
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('ifa-coop_com')



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
    linklist = []
    stores = []
    p = 0
    url = 'https://ifacountrystores.com/locations/'
    r = session.get(url, headers=headers, verify=False)  
    soup =BeautifulSoup(r.text, "html.parser")
   
    divlist = soup.findAll('div', {'class': 'store-entry'})
    logger.info(len(divlist))
    det = str(soup)
    start = 0
    for div in divlist:
        link = div.find('div',{'class':'title'}).find('a')['href']
        store = div['data-id']
        r = session.get(link, headers=headers, verify=False)  
        soup =BeautifulSoup(r.text, "html.parser")
        maindiv = soup.find('div',{'class':'entry-content'})
        title  = maindiv.find('h4').text
        maindiv = maindiv.find('p').text
        address = maindiv[0:maindiv.find('Store Hours:')].replace('\n','').replace('\r','')
        hours = maindiv[maindiv.find('Store Hours:'):maindiv.find('Phone Number:')]
        phone = maindiv[maindiv.find('Phone Number:'): len(maindiv)]        
        #logger.info(address)
        address = usaddress.parse(address)
        i = 0
        street = ""
        city = ""
        state = ""
        pcode = ""
        while i < len(address):
            temp = address[i]
            if temp[1].find("Address") != -1 or temp[1].find("Street") != -1 or temp[1].find("Recipient") != -1 or \
                    temp[1].find("BuildingName") != -1 or temp[1].find("USPSBoxType") != -1 or temp[1].find(
                "USPSBoxID") != -1:
                street = street + " " + temp[0]
            if temp[1].find("PlaceName") != -1:
                city = city + " " + temp[0]
            if temp[1].find("StateName") != -1:
                state = state + " " + temp[0]
            if temp[1].find("ZipCode") != -1:
                pcode = pcode + " " + temp[0]
            i += 1
        logger.info('>>')
        soup = str(soup)
        start = soup.find('data-lat=')
        start = soup.find('"',start) + 1
        end =  soup.find('"',start)
        lat = soup[start:end]
        start = soup.find('data-lng=')
        start = soup.find('"',start) + 1
        end =  soup.find('"',start)
        longt = soup[start:end]
        state = state.lstrip()
        if len(state) > 3:
            state = state.split(' ')[0]
        if pcode == '':
            pcode = '<MISSING>'
        tempcity = title[0:title.find(' IFA')]
        logger.info(tempcity,city.replace(',',''))
        if tempcity.strip() != city.replace(',','').strip() and city.find('North') == -1:
            street = street + ' ' + city
            city = tempcity
        data.append(['https://ifa-coop.com/',link,                   
                        title,
                        street.lstrip().replace(',',''),
                        city.lstrip().replace(',',''),
                        state.lstrip().replace(',',''),
                        pcode.lstrip().replace(',',''),
                        'US',
                        store,
                        phone.replace('Phone Number: ','').replace('\t',''),
                        '<MISSING>',
                        lat,
                        longt,
                        hours.replace('Store Hours: ','').replace('\t','')
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
