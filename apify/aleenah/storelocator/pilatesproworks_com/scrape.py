import csv
import re
from bs4 import BeautifulSoup
import requests
from pyzipcode import ZipCodeDatabase
import time

from sgselenium import SgSelenium

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

    #res=requests.get("https://www.pilatesproworks.com/locations")
    driver.get("https://www.pilatesproworks.com/locations")
    #print(driver.page_source)
    time.sleep(1)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    divs = soup.find_all('div', {'class': 'slide sqs-gallery-design-grid-slide'})
    divs=divs[:10]
    print(len(divs))
    for div in divs:
        page_url.append("http://www.pilatesproworks.com/"+ div.find('a').get("href").split("/")[-1])

    for url in page_url:
        print(url)
        driver.get(url)
        #res= requests.get(url)
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        try:
            div = soup.find('div', {'class': "sqs-block map-block sqs-block-map"}).get("data-block-json")
            lat.append(re.findall(r'"mapLat":(-?[\d\.]*)', div)[0])
            long.append(re.findall(r'"mapLng":(-?[\d\.]*)',div)[0])
            locs.append(soup.find('h5').text)
            info = re.findall(r'(ADDRESS.*EMAIL)',soup.text,re.DOTALL)[0]
            addr= re.findall(r'ADDRESS(.*)PHONE',info)[0].replace("\xa0"," ")
            phones.append(re.findall(r'PHONE(.*)EMAIL',info)[0])
            add = addr.split(" ")
            z=add[-1]
            s=add[-2]
            zips.append(z)
            states.append(s)
            zcdb = ZipCodeDatabase()
            cz = zcdb[z]
            c= cz.place
            addr=addr.replace(z,"").replace(s,"").replace(",","").strip()
            if c in addr:
                street.append(addr.replace(c,""))
                cities.append(c)
            else:
                c = add[-3]
                street.append(addr.replace(c, ""))
                cities.append(c)

        except:#page out of order
            locs.append("<MISSING>")
            street.append("<MISSING>")
            cities.append("<MISSING>")
            states.append("<MISSING>")
            zips.append("<MISSING>")
            phones.append("<MISSING>")
            lat.append("<MISSING>")
            long.append("<MISSING>")
            #print(soup)

    all = []
    for i in range(0, len(locs)):
        row = []
        row.append("https://www.pilatesproworks.com")
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
        row.append("<MISSING>")  # timing
        row.append(page_url[i])  # page url

        if row not in all:
            all.append(row)
    return all

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
