import csv
import requests
from bs4 import BeautifulSoup
import re

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

options = Options() 
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome('chromedriver', options=options)

BASE_URL = 'https://www.shoppersfood.com'
MISSING = '<MISSING>'

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_soup(url):
    res = requests.get(url)
    return BeautifulSoup(res.content, 'html.parser')

def parse_google_maps_url(url):
    return re.findall(r'll=(-?\d*.{1}\d*,-?\d*.{1}\d*)&', url)[0].split(',')

def fetch_store_data(soup, url):
    driver.get(url)
    location_name = soup.select_one('h2.storeName').text
    street_address = soup.select_one("span[itemProp='streetAddress']").text
    city = soup.select_one("span[itemProp='addressLocality']").text
    state = soup.select_one("span[itemProp='addressRegion']").text
    zipcode = soup.select_one("span[itemProp='postalCode']").text
    store_number = re.findall(r'.(\d*).html', url)[0]
    phone = soup.select_one("a[itemProp='telephone']").text
    try:
        hours_of_operation = soup.select_one("span[itemProp='openingHours']").text
    except:
        hours_of_operation = MISSING
    google_maps_url = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='ll=']"))
    ).get_attribute('href')
    lat, lon = parse_google_maps_url(google_maps_url)
    return [BASE_URL, location_name, street_address, city, state, zipcode, 'US', store_number, phone, MISSING, lat, lon, hours_of_operation]

def fetch_data():
    data = []
    soup = fetch_soup('https://www.shoppersfood.com/stores/search-stores.html')
    state_urls = [
        BASE_URL + a_tag['href']
        for a_tag in soup.select('div.find-view-states a')
    ]
    for state_url in state_urls:
        state_soup = fetch_soup(
            state_url + '&displayCount=1000'
        )
        store_urls = [
            BASE_URL + a_tag['href']
            for a_tag in state_soup.select('a.store-detail')
        ]
        for store_url in store_urls:
            store_soup = fetch_soup(store_url)
            data.append(
                fetch_store_data(store_soup, store_url)
            )
    driver.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
