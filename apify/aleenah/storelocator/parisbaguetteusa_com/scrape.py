import csv

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome("chromedriver", options=options)

def fetch_data():

    all=[]

    driver.get('https://parisbaguette.com/locations/')
    driver.switch_to.frame(driver.find_element_by_tag_name('iframe'))
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    print(soup)
    stores = soup.find_all('div', {'class': 'com_locator_address'})
    print(len(stores))
    for store in stores:
        loc=store.find('h2').find('a').text.strip()
        street = store.find('span', {'class': 'line_item address'}).text.strip()
        city=store.find('span', {'class': 'line_item city'}).text.strip()
        state=store.find('span', {'class': 'line_item state'}).text.strip()
        zip=store.find('span', {'class': 'line_item postalcode'}).text.strip()
        phone=store.find('span', {'class': 'line_item phone'}).text.strip()


        all.append([
            "https://parisbaguette.com/",
            loc,
            street,
            city,
            state,
            zip,
            "US",
            "<MISSING>",  # store #
            phone,  # phone
            "<MISSING>",  # type
            "<MISSING>",  # lat
            "<MISSING>",  # long
            "<MISSING>",  # timing
            "https://parisbaguette.com/locations/"])

    return all

def scrape():
    data = fetch_data()
    write_output(data)

scrape()