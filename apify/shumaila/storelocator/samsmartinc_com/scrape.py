import requests
from bs4 import BeautifulSoup
import csv
import string
import re, time
import usaddress

from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('samsmartinc_com')



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
    
    url = 'https://samsmartinc.com/locations'
    r = session.get(url, headers=headers, verify=False)
  
    soup1 =BeautifulSoup(r.text, "html.parser")
   

    soup = str(soup1)
    p = 0
    start = soup.find('google.maps.LatLng',0)
    while start > -1:
        try:
            start = soup.find('google.maps.LatLng',start+4)
            start =soup.find('(',start) + 1
            end = soup.find(',',start)
            lat = soup[start:end]
            start = end + 2
            end = soup.find(')',start)
            longt =  soup[start:end]
            start = end + 2
            start=soup.find('("content"',start)
            start=soup.find(',',start) + 1
            end = soup.find(');',start)
            detail = soup[start:end]
            detail = BeautifulSoup(detail, "html.parser")
            title = detail.find('h5').text
            store = title[title.find('#')+1:len(title)]
            address = str(detail.find('p'))
            #logger.info(title,store,address)
            street = address[address.find('p>')+2:address.find('<',address.find('p>')+1)]
            
            city = address[address.find('/>')+2:address.find(',')]
            state = address[address.find(',')+2:address.find('</')]
            state=state.lstrip()
            pcode = state[state.find(' ')+1:len(state)]
            state = state[0:state.find(' ')]
            #logger.info(street,city,state,pcode)
            start = end + 1
            detail = str(soup1.find('section'))
            #logger.info(detail)
            mstart = detail.find(pcode)
            mstart = detail.find('>',mstart)+1
            mend = detail.find('<br',mstart)
            phone = detail[mstart:mend]
            if pcode == '282011':
                pcode = '28201'
            
            data.append([
                            'https://samsmartinc.com/',
                            'https://samsmartinc.com/locations',                   
                            title,
                            street,
                            city,
                            state,
                            pcode,
                            'US',
                            store,
                            phone,
                            "<MISSING>",
                            lat,
                            longt,
                            "<MISSING>"
                        ])
            logger.info(p,data[p])
            p += 1
            
        except:
            break
        
        
    return data


def scrape():
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))

scrape()
