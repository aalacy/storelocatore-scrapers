from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time
from random import randint
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('kittles_com')



def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    output_list = []
    base_link = "https://www.kittles.com/storelocations.inc"

    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
    HEADERS = {'User-Agent' : user_agent}

    session = SgRequests()
    req = session.get(base_link, headers = HEADERS)
    time.sleep(randint(1,2))
    try:
        base = BeautifulSoup(req.text,"lxml")
        logger.info("Got today page")
    except (BaseException):
        logger.info('[!] Error Occured. ')
        logger.info('[?] Check whether system is Online.')

    try:
        store_list = base.find(id="staticpagenav").find_all("li")
    except:
        req = session.get(base_link, headers = HEADERS)
        logger.info("Retrying page load ..")
        time.sleep(randint(2,4))
        try:
            base = BeautifulSoup(req.text,"lxml")            
        except (BaseException):
            logger.info('[!] Error Occured. ')
            logger.info('[?] Check whether system is Online.')
            
        store_list = base.find(id="staticpagenav").find_all("li")

    for link in store_list:
        link = "https://www.kittles.com" + link.a['href']

        req = session.get(link, headers = HEADERS)
        time.sleep(randint(1,2))
        try:
            store_base = BeautifulSoup(req.text,"lxml")
            logger.info(link)
        except (BaseException):
            logger.info('[!] Error Occured. ')
            logger.info('[?] Check whether system is Online.')

        location_name = store_base.find("h2").text.strip()
        script = store_base.find_all('script', attrs={'type': "application/ld+json"})[1].text.replace('- -', '-')
        store = json.loads(script)
        store_hours = store_base.find_all(class_="store-locations-info")[1].text.replace("Store Hours", "").strip()
        output = []
        output.append("kittles.com") #locator_domain
        output.append(link) #page_url
        output.append(location_name) #location name
        output.append(store['address']['streetAddress'].strip()) #address
        output.append(store['address']['addressLocality']) #city
        output.append(store['address']['addressRegion']) #state
        output.append(store['address']['postalCode']) #zipcode
        output.append(store['address']['addressCountry']) #country code
        output.append("<MISSING>") #store_number
        output.append(store['telephone']) #phone
        output.append(store['@type']) #location type
        output.append(str(store['geo']['latitude'])) #latitude
        output.append(str(store['geo']['longitude'])) #longitude
        output.append(store_hours) #opening hours
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
