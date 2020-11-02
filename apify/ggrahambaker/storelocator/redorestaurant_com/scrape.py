from bs4 import BeautifulSoup
import csv
import string
import re, time
import usaddress
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('redorestaurant_com')



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
    url = 'https://www.redorestaurant.com/'
    r = session.get(url, headers=headers, verify=False)  
    soup =BeautifulSoup(r.text, "html.parser")
    link_list = soup.findAll('li')
    det = ''
    cleanr = re.compile(r'<[^>]+>')
    pattern = re.compile(r'\s\s+') 
    for li in link_list:
        if li.text.lower().find('location') > -1:
            det = li
            break
    link_list = li.findAll('a')
    for link in link_list:
        if link['href'] != '#':
            title= link.text
            link = link['href']
            r = session.get(link, headers=headers, verify=False)  
            soup =BeautifulSoup(r.text, "html.parser")                  
            maindiv = soup.find('div',{'class':'et_pb_row et_pb_row_2'}).text
            maindiv = re.sub(pattern,'',maindiv).splitlines()
            address = maindiv[0].replace(',','').lstrip()
            if address.find('.RED O RESTAURANT') > -1:
                address = address.split('.RED O RESTAURANT')[1]
            else:
                address = address.replace('Red O Restaurant ','')
            address = usaddress.parse(address)
            i = 0
            street = ""
            city = ""
            state = ""
            pcode = ""
            while i < len(address):
                temp = address[i]
                if temp[1].find("Address") != -1 or temp[1].find("Street") != -1 or temp[1].find("Recipient") != -1 or temp[1].find("BuildingName") != -1 or temp[1].find("USPSBoxType") != -1 or temp[1].find(
                    "USPSBoxID") != -1:
                    street = street + " " + temp[0]
                if temp[1].find("PlaceName") != -1:
                    city = city + " " + temp[0]
                if temp[1].find("StateName") != -1:
                    state = state + " " + temp[0]
                if temp[1].find("ZipCode") != -1:
                    pcode = pcode + " " + temp[0]
                i += 1
            
            phone = maindiv[1]
            hours = maindiv[2:]
            if phone.find('TEL') == -1:
                #hours = phone
                phone = '<MISSING>'
                
            else:
                phone = phone.split('TEL ')[1].split(' ')[0]
            
            #logger.info(phone)
            
            if title.find("O Lounge") == -1:
                hours = 'Daily 11 am - 11 pm'
            else:
                hours = ' '.join(hours).replace('HOURS', 'HOURS ')
            data.append([
                        'https://www.redorestaurant.com/',link, title, street.lstrip(), city.lstrip(), state.lstrip(), pcode.lstrip(),'US','<MISSING>',phone,'<MISSING>','<MISSING>','<MISSING>',
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
