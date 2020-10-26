from bs4 import BeautifulSoup
import csv
import string
import re, time, usaddress

from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('mygatestore_com')



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
    url = 'https://www.mygatestore.com/wp-content/plugins/superstorefinder-wp/ssf-wp-xml.php?wpml_lang=&t=1599378444483'
    r = session.get(url, headers=headers, verify=False)
  
    soup =BeautifulSoup(r.text, "html.parser")
   
    storelist = soup.find('store').findAll('item')
    #logger.info("states = ",len(storelist))
    for store in storelist:
        title = store.find('location').text
        address = store.find('address').text.replace('&#44;','').strip()
        try:
            address = address.split('USA')[0]
            address1 = address
        except:
            pass
        #logger.info(address)
        address = usaddress.parse(address)
        #input()
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
        
        lat = store.find('latitude').text

        longt = store.find('longitude').text
        try:
            storeid = title.split('#')[1]
        except:
            storeid = title.split(' ')[-1]
        if len(street) < 3:
            street = address1.split(',')[0]
        if len(pcode) < 3:
            pcode = store.find('address').text.split(' ')[-1]
        data.append([
                        'https://www.mygatestore.com/',
                        'https://www.mygatestore.com/find-a-gate/',                   
                        title,
                        street,
                        city,
                        state,
                        pcode,
                        'US',
                        storeid,
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
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))

scrape()
