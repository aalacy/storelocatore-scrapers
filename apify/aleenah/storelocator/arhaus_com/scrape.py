import csv
from sgselenium import SgSelenium
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import re
from bs4 import BeautifulSoup
from sgrequests import SgRequests
import time

driver = SgSelenium().chrome()
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
    # Your scraper here
    locs = []
    street = []
    states=[]
    cities = []
    types=[]
    phones = []
    zips = []
    long = []
    lat = []
    timing = []
    ids=[]
    page_url=[]
    urls=[]
    res=session.get("https://www.arhaus.com/store/")
    soup = BeautifulSoup(res.text, 'html.parser')
    statel=re.findall(r'<a class="store-directory__link" href="([^"]+)"',str(soup))
    print(len(statel))

    for sl in statel:
        page_url.append("https://www.arhaus.com"+sl)

    for url in page_url:
        print(url)
        try:
            driver.get(url)
        except:
            driver.get(url)

        WebDriverWait(driver, 190).until(EC.presence_of_element_located((By.CLASS_NAME, 'store-details__header-heading')))
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        locs.append(soup.find('h1', {'class': 'store-details__header-heading'}).text)
        street.append(soup.find('span', {'class': 'store-details__street-address-1'}).text)
        cities.append(soup.find('span', {'class': 'store-details__street-city'}).text.strip())
        states.append(soup.find('span', {'class': 'store-details__street-state'}).text.strip())
        zips.append(soup.find('span', {'class': 'store-details__street-zip'}).text.strip())
        timing.append(soup.find_all('div', {'class': 'store-details__info-section'})[1].text.strip().replace("\n"," ").replace('Instagram Icon       Follow us on Instagram','').replace('Location Hours ','').strip())
        #print(soup.find_all('div', {'class': 'store-details__info-section'})[1].text.strip().replace("\n"," ").replace('Instagram Icon       Follow us on Instagram','').replace('Location Hours ','').strip())
        phones.append(soup.find('div', {'class': 'store-details__phone'}).text.strip())
        lat.append(re.findall(r'"latitude": (-?[\d\.]+)',str(soup))[0])
        long.append(re.findall(r'"longitude": (-?[\d\.]+)',str(soup))[0])

    all = []
    for i in range(0, len(locs)):
        row = []
        row.append("https://www.arhaus.com")
        row.append(locs[i])
        row.append(street[i])
        row.append(cities[i])
        row.append(states[i])
        row.append(zips[i])
        row.append("US")
        row.append("<MISSING>")  # store #
        row.append(phones[i])  # phone
        row.append("<MISSING>")  # type
        row.append(lat[i])  # lat
        row.append(long[i])  # long
        row.append(timing[i])  # timing
        row.append(page_url[i])  # page url

        all.append(row)
    return all

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
