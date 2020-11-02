import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sgselenium import SgSelenium
import time
from selenium.webdriver.support.wait import WebDriverWait
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('mickeythemoose_com')




session = SgRequests()



def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    driver = SgSelenium().firefox()
    driver.get("http://mickeythemoose.com/store-locator/")
    soup = BeautifulSoup(driver.page_source, "lxml")
    script = soup.find(lambda tag: (tag.name == "script") and "WPGMZA_localized_data" in tag.text).text.split("var WPGMZA_localized_data = ")[1].replace("/* ]]> */",'').replace("};","}")
    keys1 = (json.loads(script)['restnoncetable']['/marker-listing/'])
    keys2 = (json.loads(script)['restnonce'])

    base_url = "https://mickeythemoose.com"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36',
        "content-type":'application/x-www-form-urlencoded; charset=UTF-8',
        "origin": "https://mickeythemoose.com",
        "x-requested-with": "XMLHttpRequest",
        "x-wp-nonce": keys2,
        "x-wpgmza-action-nonce": keys1
    }
    r = session.post("https://mickeythemoose.com/wp-json/wpgmza/v1/marker-listing/",headers=headers,data='phpClass=WPGMZA%5CMarkerListing%5CBasicTable&start=0&length=10000&map_id=1').json()
    # logger.info(r)
    return_main_object = []
    if "meta" in r:
        for loc in r['meta']:
            page_url = loc['link']
            # logger.info(loc['link'])
            r1=session.get(loc['link'])
            name=loc['title'].strip()
            storeno=loc['id']
            lat=loc['lat']
            lng=loc['lng']
            soup=BeautifulSoup(r1.text,'lxml')
            main=list(soup.find('div',{"class":"store_info"}).find('div',{"class":"gray-box"}).stripped_strings)
            # logger.info(main)
            del main[0]
            address=main[0].strip()
            ct=main[1].split(',')
            city=ct[0].strip()
            state=ct[1].strip().split(' ')[0].strip()
            zip=ct[1].strip().split(' ')[1].strip()
            phone=main[2].strip()
            del main[0]
            del main[0]
            del main[0]
            del main[0]
            del main[0]
            hour=' '.join(main).replace('–>','').strip()
            country="US"
            store=[]
            store.append(base_url)
            store.append(name if name else "<MISSING>")
            store.append(address if address else "<MISSING>")
            store.append(city if city else "<MISSING>")
            store.append(state if state else "<MISSING>")
            store.append(zip if zip else "<MISSING>")
            store.append(country if country else "<MISSING>")
            store.append(storeno if storeno else "<MISSING>")
            store.append(phone if phone else "<MISSING>")
            store.append("<MISSING>")
            store.append(lat if lat else "<MISSING>")
            store.append(lng if lng else "<MISSING>")
            store.append(hour if hour else "<MISSING>")
            store.append(page_url)


            # logger.info("data ==== "+str(store))
            # logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
