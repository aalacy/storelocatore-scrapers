import json

import sgzip
from Scraper import Scrape
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


URL = "https://pharmacy.kmart.com"


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
        stores = []
        seen = []

        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(self.CHROME_DRIVER_PATH, options=options)
        zipcodes = sgzip.for_radius(50) + ["25304", "03784"]

        for zip_search in sgzip.for_radius(50):
            url = f"https://pharmacy.kmart.com/RxServices/kmartrx/fetchPharmFinderGB?finderInput={zip_search}"
            driver.get(url)
            stores.extend(json.loads(driver.find_element_by_css_selector("pre").text))

        for store in stores:
            if store["unitNumber"] not in seen:
                # Store ID
                location_id = store["unitNumber"]

                # Name
                location_title = store["name"]

                # Street
                street_address = store["address"]

                # Country
                country = "US"

                # State
                state = store["state"]

                # city
                city = store["city"]

                # zip
                zipcode = store["zipcode"]

                # Lat
                lat = store["latitude"]

                # Long
                lon = store["longitude"]

                # Phone
                phone = store["storePhoneNumber"]

                # hour
                hour = store["pharmacyHours"]

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
                seen.append(store["unitNumber"])

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
        ):
            if location_id not in seen:
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
                        "<MISSING>",
                        latitude,
                        longitude,
                        hour,
                    ]
                )
                seen.append(location_id)


scrape = Scraper(URL)
scrape.scrape()
