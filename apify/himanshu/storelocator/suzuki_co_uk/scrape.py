
import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.wait import WebDriverWait
import re
import json
import time
import sgzip
import requests
session = SgRequests()
import platform
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('suzuki_co_uk')


system = platform.system()

def write_output(data):
    with open('data.csv', mode='w', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def get_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    return webdriver.Firefox(executable_path='geckodriver', options=options)        

def fetch_data(): 
    base_url = "https://www.suzuki.co.uk/"
    addressess = []
    search = sgzip.ClosestNSearch() # TODO: OLD VERSION [sgzip==0.0.55]. UPGRADE IF WORKING ON SCRAPER!
    search.initialize(country_codes = ["gb"])
    MAX_RESULTS = 50
    MAX_DISTANCE = 50
    current_results_len = 0     # need to update with no of count.
    zip_code = search.next_zip()

    driver = get_driver()
    while zip_code:
        
        result_coords = []
        driver.get("https://cars.suzuki.co.uk/find-a-dealer/")
        try:
            WebDriverWait(driver, 10).until(lambda x:x.find_element_by_xpath('//*[@id="onetrust-close-btn-container"]/a')).click()
        except:
            pass
        driver.execute_script("window.scrollTo(0, 300)") 
        WebDriverWait(driver, 10).until(lambda x:x.find_element_by_xpath('//*[@id="PostcodeForDealers"]')).send_keys(zip_code)
        time.sleep(5)
        WebDriverWait(driver, 10).until(lambda x:x.find_element_by_xpath('//button[contains(text(),"Search")]')).click()

        time.sleep(10)
        soup = bs(driver.page_source, "lxml")
        current_results_len = len(soup.find_all("a",{"class":re.compile("button button--primary button--block")}))
        for url in soup.find_all("a",{"class":re.compile("button button--primary button--block")}):
            page_url = "https://cars.suzuki.co.uk" + url['href']

            location_soup = bs(requests.get(page_url).text, "lxml")
            location_name = location_soup.find("span",{"class":"heading-set__line heading-set__main"}).text
            
            if location_soup.find("a",{"class":re.compile("button button--primary button--primary-dealer-detail call--mobile")}):
                phone = location_soup.find("a",{"class":re.compile("button button--primary button--primary-dealer-detail call--mobile")})['data-phone']
            else:
                phone = location_soup.find("div",{"class":"address__location"}).find_all("p")[1].text.replace("Main Phone:","").replace("Dealership Number:","").strip()
            
            addr = list(location_soup.find("div",{"class":"address__location"}).find("p").stripped_strings)
            state = ''
            zipp = ''
            for postal in addr[-1].replace("-","").replace("&","").replace("/","").split():
                if postal.isalpha():
                    state+= " "+ postal
                else:
                    zipp+= " "+ postal  
            street_address = addr[0]
            if len(addr) == 2:
                city = "<MISSING>"
            else:
                city = addr[1]
            lat = location_soup.find("div",{"class":"google-map"})['data-pin-lat']
            lng = location_soup.find("div",{"class":"google-map"})['data-pin-lng']
            if location_soup.find("div",{"id":"tab_sales"}):
                hours = " ".join(list(location_soup.find("div",{"id":"tab_sales"}).stripped_strings))
            elif location_soup.find("div",{"id":"tab_desktop_Sales"}):
                hours = " ".join(list(location_soup.find("div",{"id":"tab_desktop_Sales"}).stripped_strings))
            else:
                hours = "<MISSING>"
        
            result_coords.append((lat,lng))        
            store = []
            store.append(base_url)
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zipp)   
            store.append("UK")
            store.append("<MISSING>")
            store.append(phone)
            store.append("<MISSING>")
            store.append(lat)
            store.append(lng)
            store.append(hours)
            store.append(page_url)     
        
            store = [str(x).strip() if x else "<MISSING>" for x in store]
            if store[2] in addressess:
                continue
            addressess.append(store[2])
            # logger.info(store)
            # logger.info("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            yield store
            
        if current_results_len < MAX_RESULTS:
            # logger.info("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif current_results_len == MAX_RESULTS:
            # logger.info("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        zip_code = search.next_zip()
    
    
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
