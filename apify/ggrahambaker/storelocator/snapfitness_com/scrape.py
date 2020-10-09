from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time
import re
from random import randint

from sgselenium import SgSelenium
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from sglogging import sglog

log = sglog.SgLogSetup().get_logger(logger_name="snapfitness.com")

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    locator_domain = 'https://www.snapfitness.com/'

    driver = SgSelenium().chrome()
    time.sleep(2)

    urls = ['https://www.snapfitness.com/ca/gyms/?q=canada', 'https://www.snapfitness.com/us/gyms/?q=united%20states']
    
    link_list = []
    for url in urls:

        driver.get(url)
        time.sleep(randint(2,4))

        element = WebDriverWait(driver, 50).until(EC.presence_of_element_located(
            (By.CLASS_NAME, "address")))
        time.sleep(randint(2,4))
        
        locs = driver.find_elements_by_css_selector('.club-overview.Highlight0')
        
        for loc in locs:
            href = loc.find_element_by_css_selector('a.btn.btn-primary').get_attribute('href')
            if href not in link_list:
                link_list.append(href)

    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
    HEADERS = {'User-Agent' : user_agent}

    session = SgRequests()

    all_store_data = []
    total_links = len(link_list)
    log.info("Processing " + str(total_links) + " links...")
    for i, link in enumerate(link_list):
        # print("Link %s of %s" %(i+1,total_links))

        req = session.get(link, headers = HEADERS)
        base = BeautifulSoup(req.text,"lxml")
        # print(link)
                
        main = base.find(class_='location')
        try:
            location_name = main.h1.text
        except:
            location_name = main.h3.text

        try:
            phone_number = base.find(class_="details").find_all("li")[0].text.strip()
            addy = str(base.find(class_="details").find_all("li")[1].span)
            if "Snap" in phone_number:
                phone_number = base.find(class_="details").find_all("li")[1].text.strip()
                addy = str(base.find(class_="details").find_all("li")[2].span)
            if not phone_number:
                phone_number = '<MISSING>'
        except:
            phone_number = '<MISSING>'
            
        
        addy = addy.replace('<span>',"").replace('</span>',"").strip().split('<br/>')

        if '/ca/' in link:
            country_code = 'CA'
        else:
            country_code = 'US'

        street_address = addy[0].strip().replace(" ,",",").replace("&amp;","&")
        street_address = (re.sub(' +', ' ', street_address)).strip()

        zip_code = addy[1][-5:]
        if " " in zip_code:
            zip_code = addy[1][-7:].strip()

        else:
            if not zip_code.isnumeric():
                zip_code = addy[1][addy[1].rfind(' '):].strip()

        state = addy[1][addy[1].find(zip_code)-3:addy[1].find(zip_code)].strip()
        city = addy[1][:addy[1].rfind(state)].strip()

        if city == "Cary N":
            city = "Cary"
            state = "NC"

        google_href = base.find(id='map')['href']
        
        start = google_href.find('&query=')
        coords = google_href[start + len('&query='):].split(',')

        lat = coords[0]
        longit = coords[1]

        try:
            hours = base.find(class_='staff-days').text.replace("\n\n\n"," ").replace("\n"," ").strip()
            if not hours:
                hours = '<MISSING>'
        except:
            hours = '<MISSING>'
        
        location_type = '<MISSING>'
        page_url = link

        store_number = '<MISSING>'

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                        store_number, phone_number, location_type, lat, longit, hours, page_url]
        
        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
