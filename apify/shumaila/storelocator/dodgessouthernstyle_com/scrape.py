import requests
from bs4 import BeautifulSoup
import csv
import string
import re, time
import usaddress

from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('dodgessouthernstyle_com')



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
    url = 'https://dodgessouthernstyle.com/locations/'
    r = session.get(url, headers=headers, verify=False)
  
    soup =BeautifulSoup(r.text, "html.parser")
    div_list = soup.findAll('div',{'class':'vc_tta-panel'})
    logger.info(len(div_list))
    for div in div_list:
        try:
            title = div.find('span',{'class':'vc_tta-title-text'}).text
            detail = div.findAll('li')
            store = detail[0].text
            store = store[store.find('#')+1:len(store)]
            phone = detail[1].text
            address = detail[2].text
            address = address.lstrip()
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
            city = city.lstrip()
            city = city.replace(",",'')
            street = street.replace(",",'')
            street = street.lstrip()
            state = state.lstrip()
            pcode = pcode.lstrip()

            if len(city) < 2:
                city = "<MISSING>"
            if len(street) < 2:
                street = "<MISSING>"
            if len(state) < 2:
                state = "<MISSING>"
            if len(pcode) < 2:
                pcode = "<MISSING>"
            if len(phone) < 2:
                    phone =  "<MISSING>"
            state = state.replace(',','')
            if phone.find('00354') > -1:
                phone = phone.replace('00354','0354')
            data.append([
                                'https://dodgessouthernstyle.com/',
                                'https://dodgessouthernstyle.com/locations/',                   
                                title,
                                street,
                                city,
                                state,
                                pcode,
                                'US',
                                store,
                                phone,
                                "<MISSING>",
                                "<MISSING>",
                                "<MISSING>",
                                "<MISSING>"
                            ])
            #logger.info(p,data[p])
            p += 1
            
        except:
            pass

    
        
    return data


def scrape():
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))

scrape()
