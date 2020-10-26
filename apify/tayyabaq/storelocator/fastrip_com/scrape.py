from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time
from random import randint
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('fastrip_com')




def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def get_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    return webdriver.Chrome('chromedriver', chrome_options=options)

def fetch_data():

    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
    headers = {'User-Agent' : user_agent}

    session = SgRequests()

    data=[]; location_name=[];location_type=[];address_stores=[]; city=[];street_address=[];store_number=[]; zipcode=[]; state=[]; latitude=[]; longitude=[]; hours_of_operation=[]; phone=[]
    driver = get_driver()
    driver.get('http://fastrip.com/index.php/store-locations')
    time.sleep(3)
    driver.find_element_by_xpath('//select[@id="radiusSelect"]/option[5]').click()
    time.sleep(2)
    stores = driver.find_elements_by_class_name('loc-address')

    for n in range(0,len(stores)):
        logger.info("Store " + str(n+1) + " of " + str(len(stores)))
        try:
            raw_address = stores[n].text.replace("Lake Isabella CA","Lake Isabella, CA")
            state.append(raw_address.split(",")[2].split()[0].split(".")[0].upper())
            city.append(raw_address.split(",")[1].strip())
            street = raw_address.split(",")[0]
            street_address.append(street)
            try:
                if street == "2199 Hwy 95":
                    zipcode.append("86442")
                else:
                    zipcode.append(raw_address.split(",")[2].split()[1])
            except:
                zipcode.append(raw_address.split(",")[3].strip())
        except:
            a=' '.join(stores[n].text.split(".")[1:])
            state.append(a.split()[-2].strip().split(".")[0].upper())
            city.append(a.split()[-3].split(",")[0].strip())
            street = stores[n].text.split(".")[0]
            street_address.append(street)
            if street == "2199 Hwy 95":
                zipcode.append("86442")
            else:
                zipcode.append(a.split()[-1].strip())

        try:
            stores[n].click()
            time.sleep(randint(1,3))
            map_link = driver.find_element_by_class_name("infoloc-directions").find_element_by_tag_name("a").get_attribute("href")
        except:
            map_link = ""

        if map_link:
            req = session.get(map_link, headers = headers)
            time.sleep(randint(1,2))
            try:
                maps = BeautifulSoup(req.text,"lxml")
            except (BaseException):
                logger.info('[!] Error Occured. ')
                logger.info('[?] Check whether system is Online.')

            try:
                raw_gps = maps.find('meta', attrs={'itemprop': "image"})['content']
                lat = raw_gps[raw_gps.find("=")+1:raw_gps.find("%")].strip()
                longit = raw_gps[raw_gps.find("-"):raw_gps.find("&")].strip()

                if len(lat) < 5:
                    lat = "<MISSING>"
                    longit = "<MISSING>"
            except:
                lat = "<MISSING>"
                longit = "<MISSING>"
        else:            
            lat = "<MISSING>"
            longit = "<MISSING>"

        latitude.append(lat)
        longitude.append(longit)

    loc = driver.find_elements_by_class_name('loc-name')
    location_name = [loc[n].text for n in range(0,len(loc))]
    tags = driver.find_elements_by_class_name("result-inner")
    for n in range(0,len(tags)):
        try:
            loc_type = tags[n].find_element_by_class_name("loc-tags").text.replace("Tags:","").strip()
            location_type.append(loc_type)
        except:
            if "gas" in location_name[n].lower():
                location_type.append("Gas")
            else:
                location_type.append("OTHER")


    store_number= [loc[n].text.split("#")[1].strip() for n in range(0,len(loc))]
    phones = driver.find_elements_by_class_name('loc-phone')
    phone = [phones[n].text for n in range(0,len(phones))]
    for n in range(0,len(street_address)):
        data.append([
            'http://fastrip.com',
            'http://fastrip.com/index.php/store-locations',
            location_name[n],
            street_address[n],
            city[n],
            state[n],
            zipcode[n],
            'US',
            store_number[n],
            phone[n],
            location_type[n],
            latitude[n],
            longitude[n],
            '<MISSING>'
        ])
    driver.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)
   
scrape()
