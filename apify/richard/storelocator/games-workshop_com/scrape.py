from sgselenium import SgSelenium
from bs4 import BeautifulSoup
import time
import json
import re

from Scraper import Scrape

# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options

# def get_driver():
#     options = Options() 
#     options.add_argument('--headless')
#     options.add_argument('--no-sandbox')
#     options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36")
#     options.add_argument('--disable-dev-shm-usage')
#     options.add_argument('--window-size=1920,1080')
#     return webdriver.Chrome('chromedriver', chrome_options=options)

URL = "https://www.games-workshop.com/"


class Scraper(Scrape):
    def __init__(self, url):
        Scrape.__init__(self, url)
        self.data = []

    def fetch_data(self):
        # store data
        locations_ids = []
        locations_titles = []
        street_addresses = []
        cities = []
        store_type_list = []
        states = []
        zip_codes = []
        latitude_list = []
        longitude_list = []
        phone_numbers = []
        hours = []
        countries = []
        stores = []
        links = []
        seen = []

        driver = SgSelenium().chrome()
        # driver = get_driver()
        time.sleep(2)

        base_link = "https://www.games-workshop.com/en-US/store/fragments/resultsJSON.jsp?latitude=40.2475923&radius=20000&longitude=-77.03341790000002"
        driver.get(base_link)
        time.sleep(15)

        base = BeautifulSoup(driver.page_source,"lxml")
        stores = json.loads(base.text)['locations']

        for store in stores:
            if store['type'] == 'independentRetailer':
                continue

            # Country
            country = store['country'] if 'country' in store.keys() else '<MISSING>'
            if country not in ["CA","US"]:
                continue

            # Store ID
            location_id = store['storeId'] if 'storeId' in store.keys() else store['id'].split("-")[-1]

            # Name
            location_title = store["name"].encode("ascii", "replace").decode().replace("?","-") if 'name' in store.keys() else '<MISSING>'

            # Street
            try:
                street_address = store['address1'] + " " + store['address2']
            except:
                street_address = store['address1']

            street_address = (re.sub(' +', ' ', street_address)).strip()
            digit = re.search("\d", street_address).start(0)
            if digit != 0:
                street_address = street_address[digit:]

            # State
            state = store['state'] if 'state' in store.keys() else '<MISSING>'

            # city
            city = store['city'] if 'city' in store.keys() else '<MISSING>'

            # zip
            zipcode = store['postalCode'].replace(" -","-").replace("L24R 3N1","L2R 3N1") if 'postalCode' in store.keys() else '<MISSING>'
            if len(zipcode) == 4:
                zipcode = "0" + zipcode

            # store type
            store_type = store['type'] if 'type' in store.keys() else '<MISSING>'

            # Lat
            lat = store['latitude'] if 'latitude' in store.keys() else '<MISSING>'

            # Long
            lon = store['longitude'] if 'longitude' in store.keys() else '<MISSING>'
            if lon == -76593137.0:
                lon = -76.593137

            # Phone
            phone = store['telephone'] if 'telephone' in store.keys() else '<MISSING>'
            if phone[:2] == "00":
                phone = phone[2:]
            if len(phone) < 8:
                phone = '<MISSING>'
            # hour
            hour = '<MISSING>'

            link = "https://www.games-workshop.com/en-" + country + "/" + store['seoUrl']

            # Store data
            locations_ids.append(location_id)
            store_type_list.append(store_type)
            locations_titles.append(location_title)
            street_addresses.append(street_address)
            states.append(state)
            zip_codes.append(zipcode)
            hours.append(hour)
            latitude_list.append(lat)
            longitude_list.append(lon)
            phone_numbers.append(phone)
            cities.append(city)
            countries.append(country)
            links.append(link)

        for (   
                link,
                locations_title,
                street_address,
                city,
                state,
                zipcode,
                phone_number,
                latitude,
                longitude,
                hour,
                location_id,
                country,
                store_type
        ) in zip(
            links,
            locations_titles,
            street_addresses,
            cities,
            states,
            zip_codes,
            phone_numbers,
            latitude_list,
            longitude_list,
            hours,
            locations_ids,
            countries,
            store_type_list
        ):
            if location_id not in seen:
                self.data.append(
                    [
                        self.url,
                        link,
                        locations_title,
                        street_address,
                        city,
                        state,
                        zipcode,
                        country,
                        location_id,
                        phone_number,
                        store_type,
                        latitude,
                        longitude,
                        hour,
                    ]
                )
                seen.append(location_id)



scrape = Scraper(URL)
scrape.scrape()
