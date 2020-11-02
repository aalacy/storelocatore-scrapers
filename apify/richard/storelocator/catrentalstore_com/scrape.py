import json

from Scraper import Scrape
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

URL = "https://www.catrentalstore.com/"


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
        states = []
        zip_codes = []
        latitude_list = []
        longitude_list = []
        phone_numbers = []
        hours = []
        countries = []
        location_types = []
        stores = []

        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(self.CHROME_DRIVER_PATH, options=options)

        # Fetch stores from location menu
        location_url = "https://cat-ms.esri.com/dls/cat/locations/en?f=json&forStorage=false&distanceUnit=mi&searchType=address&searchValue=USA&maxResults=50&productDivId=2%2C1%2C6&appId=GdeKAczdmNrGwdPo"
        driver.get(location_url)
        stores = json.loads(driver.find_element_by_css_selector("pre").text)

        for store in stores:
            # Store ID
            location_id = store["dealerId"]

            # Name
            location_title = store["dealerName"]

            # Type
            location_type = store["type"]

            # Street
            street_address = (
                    store["siteAddress"] + " " + store["siteAddress1"]
            ).strip()

            # Country
            country = store["countryCode"]

            # State
            state = store["siteState"]

            # city
            city = store["siteCity"]

            # zip
            zipcode = store["sitePostal"]

            # Lat
            lat = store["latitude"]

            # Long
            lon = store["longitude"]

            # Phone
            phone = store["locationPhone"]

            # hour
            hour_dict = {}
            for key in store["stores"][0].keys():
                if "storeHours" in key:
                    hour_dict[key] = store["stores"][0][key]

            hour = " ".join([day + " " + hour for day, hour in hour_dict.items()])

            # Store data
            locations_ids.append(location_id)
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
            location_types.append(location_type)

        for (
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
                location_type,
        ) in zip(
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
            location_types,
        ):
            self.data.append(
                [
                    self.url,
                    locations_title,
                    street_address,
                    city,
                    state,
                    zipcode,
                    country,
                    location_id,
                    phone_number,
                    location_type,
                    latitude,
                    longitude,
                    hour,
                ]
            )

        driver.quit()


scrape = Scraper(URL)
scrape.scrape()
