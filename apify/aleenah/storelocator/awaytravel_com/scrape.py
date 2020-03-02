import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import re

options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome("chromedriver", options=options)


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",
                         "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


session = SgRequests()


def fetch_data():
    # Your scraper here

    page_url = []
    con="US"
    res=session.get("https://www.awaytravel.com/ca/en/")
    soup = BeautifulSoup(res.text, 'html.parser')
    stores = soup.find_all('li', {'class': 'component menu-dropdown-item-component component---2m_tC'})
    all=[]
    for store in stores:
        url="https://www.awaytravel.com"+store.find('a').get('href')
        print(url)
        if "london" in url:
            con="UK"
        else:
            con="US"
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        #print(soup)
        ll = soup.find('div', {'class': 'store__map js-map'}).get('data-map')
        loc=soup.find('h1', {'class': 'heading--1'}).text
        lat=re.findall(r'"lat": (-?[\d\.]*)',ll)[0]
        long=re.findall(r'"lng": (-?[\d\.]*)',ll)[0]
        street=soup.find('span', {'itemprop': 'streetAddress'}).text
        city=soup.find('span', {'itemprop': 'addressLocality'}).text
        state=soup.find('span', {'itemprop': 'addressRegion'}).text
        zip=soup.find('span', {'itemprop': 'postalCode'}).text
        tim=""
        tims=soup.find_all('span', {'itemprop': 'openingHours'})

        for t in tims:
            tim+=t.text.strip()+" "
        if tim=="":
                tim="<MISSING>"
        all.append([
            "https://www.awaytravel.com",
            loc,
            street,
            city.replace(",",""),
            state,
            zip,
            con,
            "<MISSING>",  # store #
            "<MISSING>",  # phone
            "<MISSING>",  # type
            lat,  # lat
            long,  # long
            tim.strip().replace("   "," "),  # timing
            url])

    return all


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
