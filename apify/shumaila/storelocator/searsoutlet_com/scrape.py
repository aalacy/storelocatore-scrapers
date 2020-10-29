#https://www.sears.com/stores.html

from bs4 import BeautifulSoup
import csv
import string
import re, time
import requests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('searsoutlet_com')




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
    links = []
    p = 1
    pattern = re.compile(r'\s\s+')
    url = "https://www.searsoutlet.com/br/api/stores?_=1578134784196"
    page = requests.get(url)
    page = page.text
    flag = True
    start = 0
    i = 0
    while flag:
        start = page.find('storeName',start)
        if start == -1:
            flag = False
        else:
            start = page.find(':',start)+1
            end = page.find(',',start)
            title = page[start:end]
            title = title.replace('"',"")            
            start = end
            start = page.find('"streetAddr"',start)
            start = page.find(':',start)+1
            end = page.find(',',start)
            street = page[start:end]
            street = street.replace('"',"")            
            start = end
            start = page.find('"city"',start)
            start = page.find(':',start)+1
            end = page.find(',',start)
            city = page[start:end]
            city = city.replace('"',"")            
            start = end
            start = page.find('"state"',start)
            start = page.find(':',start)+1
            end = page.find(',',start)
            state = page[start:end]
            state = state.replace('"',"")            
            start = end
            start = page.find('"zip"',start)
            start = page.find(':',start)+1
            end = page.find(',',start)
            pcode = page[start:end]
            pcode = pcode.replace('"',"")            
            start = end
            start = page.find('"phone"',start)
            start = page.find(':',start)+1
            end = page.find(',',start)
            phone = page[start:end]
            phone = phone.replace('"',"")            
            start = end
            start = page.find('"streetAddr2"',start)
            start = page.find(',',start)+1
            end = page.find('"storeIndex"',start)-1
            hours = page[start:end]
            hours = hours.replace('"',"")
            hours = hours.replace("Hours","")
            start = end
            start = page.find('"storeIndex"',start)
            start = page.find(':',start)+1
            end = page.find(',',start)
            store = page[start:end]
            store = store.replace('"',"")            
            start = end
            start = page.find('"url"',start)
            start = page.find(':',start)+1
            end = page.find(',',start)
            link = page[start:end]
            link = link.replace('"',"")
            link = 'https://www.searsoutlet.com'+link
            page2 = requests.get(link)
            page2 = page2.text
            start1 = page2.find('"latitude"')
            start1 = page2.find(':',start1)+1
            end1 = page2.find(',',start1)
            lat = page2[start1:end1]
            start1 = page2.find('"longitude"')
            start1 = page2.find(':',start1)+1
            end1 = page2.find(',',start1)
            longt = page2[start1:end1]
            longt = longt[0:longt.find('\n')]
            lat = lat.replace('"','')
            longt = longt.replace('"','')
            
            data.append([
             'https://www.searsoutlet.com/',
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
            #logger.info(data[i])
            i += 1
            start = end
            
            
            
  

    return data

def scrape():
    data = fetch_data()
    write_output(data)
    #5:46

scrape()

