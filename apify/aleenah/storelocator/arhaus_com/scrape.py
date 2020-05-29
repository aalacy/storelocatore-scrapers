import csv
from sgselenium import SgSelenium
import re
from bs4 import BeautifulSoup
import requests
import time


driver = SgSelenium().chrome()

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
    res=requests.get("https://www.arhaus.com/store/")
    soup = BeautifulSoup(res.text, 'html.parser')
    statel=soup.find_all('a',{'class':'store_locator-store--name js-state'}, href=True)

    for sl in statel:
        urls.append(sl.get('href'))

    for sl in urls:
        driver.get("https://www.arhaus.com/store/"+sl)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        statel = soup.find_all('a', {'class': 'store_locator-store--name js-store'})
        for l in statel:
            page_url.append(l.get("href"))

    for url in page_url:
        driver.get("https://www.arhaus.com"+url)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        locs.append(soup.find('h1', {'class': 'store_locator-h1'}).text)
        street.append(soup.find('span', {'class': 'store_info-address'}).text)
        cities.append(soup.find('span', {'class': 'js-store-city'}).text.strip())
        states.append(soup.find('span', {'class': 'js-store-state'}).text.strip())
        zips.append(soup.find('span', {'class': 'js-store-zip'}).text.strip())
        timing.append(soup.find('div', {'class': 'store_hours-container'}).text.strip().replace("\n"," "))
        phones.append(soup.find('a', {'class': 'store_info-phone'}).text.strip())

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
        row.append("<MISSING>")  # lat
        row.append("<MISSING>")  # long
        row.append(timing[i])  # timing
        row.append("https://www.arhaus.com"+page_url[i])  # page url

        all.append(row)
    return all


def scrape():
    data = fetch_data()
    write_output(data)


scrape()


