from sgrequests import SgRequests
from sgselenium import SgSelenium
from bs4 import BeautifulSoup
import csv
import time
from random import randint
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('liquidhighway_com')




def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    output_list = []
    url = "http://liquidhighway.com/"

    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
    HEADERS = {'User-Agent' : user_agent}

    session = SgRequests()
    req = session.get(url, headers = HEADERS)
    time.sleep(randint(1,2))
    try:
        base = BeautifulSoup(req.text,"lxml")
        logger.info("Got today page")
    except (BaseException):
        logger.info('[!] Error Occured. ')
        logger.info('[?] Check whether system is Online.')

    store_data = base.find(id="about")
    stores = store_data.find_all("h4")
    maps = store_data.find_all(class_="mapouter")

    driver = SgSelenium().chrome()
    driver.get(url)
    time.sleep(randint(15,20))

    for i in range(len(stores)):

        map_frames = driver.find_elements_by_tag_name("iframe")
        map_frame = map_frames[i]
        driver.switch_to.frame(map_frame)
        time.sleep(randint(1,2))
        map_str = driver.page_source
        geo = re.findall(r'\[[0-9]{2}\.[0-9]+,-[0-9]{2}\.[0-9]+\]', map_str)[0].replace("[","").replace("]","").split(",")

        if i == 0:
            driver.get(url)
            time.sleep(randint(10,12))

        store = stores[i]
        raw_data = str(store)[4:-5].split("<br/>")
        raw_street = raw_data[1].split(",")[0].strip()
        output = []
        output.append("liquidhighway.com") # locator_domain
        output.append(url) # page_url
        output.append("Liquid Highway " + raw_data[0].strip()) #location name
        output.append(raw_street[:raw_street.rfind(".")+1].strip()) #address
        output.append(raw_street[raw_street.rfind(".")+1:].strip()) #city
        output.append(raw_data[1].split(",")[1].strip().split(' ')[0]) #state
        output.append(raw_data[1].split(",")[1].strip().split(' ')[1]) #zipcode
        output.append('US') #country code
        output.append("<MISSING>") #store_number
        output.append(raw_data[-1].strip()) #phone
        output.append("<MISSING>") #location type
        output.append(geo[0]) #latitude
        output.append(geo[1]) #longitude
        output.append("<MISSING>") #opening hours
        output_list.append(output)

    driver.quit()
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
