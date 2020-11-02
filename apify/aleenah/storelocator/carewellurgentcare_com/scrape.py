import csv
import re
from bs4 import BeautifulSoup
import requests
import time
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('carewellurgentcare_com')



headers={"user-agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36"}

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

    res = requests.get("https://www.carewellurgentcare.com/centers/",headers=headers)
    time.sleep(0.1)
    soup = BeautifulSoup(res.text, 'html.parser')
    #logger.info(soup)
    divs = soup.find_all('div', {'class': 'centers-list'})
    latlng= soup.find('div', {'id': 'et-main-area'}).find("script").text
    #logger.info(latlng)
    for div in divs:

        locs.append(div.find('div', {'class': 'center-name'}).text)
        addr=div.find('div', {'class': 'center-address'}).text
        timing.append(div.find('div', {'class': 'center-hours'}).text.replace("\n"," ").replace("\r"," "))
        #logger.info(div.find('div', {'class': 'center-hours'}).text.replace("\n"," ").replace("\r"," "))
        addr=addr.split("\n")
        street.append(addr[0].strip())
        addr=addr[1].split(",")
        cities.append(addr[0])
        addr=addr[1].strip().split(" ")
        states.append(addr[0])
        z= re.findall(r'[0-9]{5}',addr[1])[0]
        zips.append(z)
        phones.append(addr[1].replace(z,""))

    lat = re.findall(r'"lat":"([^"]*)"',latlng)
    long = re.findall(r'"lng":"([^"]*)"', latlng)
    ids = re.findall(r'"id":([0-9]+)', latlng)

    all = []
    for i in range(0, len(locs)):
        row = []
        row.append("https://www.carewellurgentcare.com")
        row.append(locs[i])
        row.append(street[i])
        row.append(cities[i])
        row.append(states[i])
        row.append(zips[i])
        row.append("US")
        row.append(ids[i])  # store #
        row.append(phones[i])  # phone
        row.append("<MISSING>")  # type
        row.append(lat[i])  # lat
        row.append(long[i])  # long
        row.append(timing[i])  # timing
        row.append("https://www.carewellurgentcare.com/centers/")  # page url

        all.append(row)
    return all

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
