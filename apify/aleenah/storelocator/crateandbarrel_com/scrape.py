import csv

import re
from bs4 import BeautifulSoup
import time
import requests
import os
from torrequest import TorRequest


"""options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--window-size=1920,1080')
options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36")
driver = webdriver.Chrome("chromedriver", options=options)"""


session = requests.Session()

session.trust_env=False
proxy_password = os.environ["PROXY_PASSWORD"]
proxy_url = "http://auto:{}@proxy.apify.com:8000/".format(proxy_password)
proxies = {
    'http': proxy_url,
    'https': proxy_url
}
session.proxies = proxies
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }
"""def scroll(q):
    height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(q)

        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == height:
            break
        height = new_height"""


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
    countries = []
    types=[]
    phones = []
    zips = []
    long = []
    lat = []
    timing = []
    ids=[]
    page_url=[]
    state_url=[]
    urls=["https://www.crateandbarrel.com/stores/list-province/canada-stores","https://www.crateandbarrel.com/stores/list-state/retail-stores"]

    for url in urls:
        print(url)
        print("HERE")
        session.get(url, headers=headers)
        #time.sleep(2)
        print("HERE2")
        print(session.driver.page_source)


        s=session.driver.execute_script("return Crate.Model.StateList")
        #driver.close()
        for a in s:
            print(a)
            if "canada" in url:
                state_url.append("https://www.crateandbarrel.com/stores/list-province/canada-stores/"+a['Key'])
            else:
                state_url.append("https://www.crateandbarrel.com/stores/list-state/retail-stores/"+a['Key'])






    for url in state_url:

        print(url)
        session.get(url, headers=headers)
        time.sleep(2)
        #scroll()
        stores=session.driver.execute_script("return Crate.Model.StoreList")
        times=session.driver.find_elements_by_class_name("hours")
        #driver.close()
        for yim in times:
            timing.append(yim.text.replace("\n"," "))

        for store in stores:

            ids.append(store["StoreNumber"])
            locs.append(store['Name'])
            phones.append(store['PhoneAreacode']+"-"+store['PhonePrefix']+'-'+store['PhoneSuffix'])
            cities.append(store['City'])
            states.append(store['State'])
            zips.append(store['Zip'])
            street.append(store['Address1']+store['Address2'])
            lat.append(store['StoreLat'])
            long.append(store['StoreLong'])
            if "canada" in url:
                countries.append("CA")
            else:
                countries.append("US")
            page_url.append(url)

    all = []
    for i in range(0, len(locs)):
        row = []
        row.append("https://www.crateandbarrel.com")
        row.append(locs[i])
        row.append(street[i])
        row.append(cities[i])
        row.append(states[i])
        row.append(zips[i])
        row.append(countries[i])
        row.append(ids[i])  # store #
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