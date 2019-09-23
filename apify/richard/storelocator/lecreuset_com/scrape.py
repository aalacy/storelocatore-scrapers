import json

from Scraper import Scrape
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait


URL = "https://www.lecreuset.com"


class Scraper(Scrape):
    def __init__(self, url):
        Scrape.__init__(self, url)
        self.data = []
        self.exceptions = {
            "37677": {"city": "Simpsonville", "state": "KY", "zip_code": "40067"}
        }

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

        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(self.CHROME_DRIVER_PATH, options=options)

        # Fetch stores from location menu
        location_url = "https://www.lecreuset.com/ustorelocator/location/searchJson/"
        driver.get(location_url)
        stores.extend(
            json.loads(driver.find_element_by_css_selector("pre").text)["markers"]
        )

        # Wait until element appears - 10 secs max
        wait = WebDriverWait(driver, 10)
        wait.until(ec.visibility_of_element_located((By.CSS_SELECTOR, "pre")))

        for store in stores:
            # Store ID
            location_id = store["location_id"]

            # Name
            location_title = store["title"]

            if location_id in self.exceptions:
                # City
                city = self.exceptions[location_id]["city"]

                # State
                state = self.exceptions[location_id]["state"]

                # Zip
                zip_code = self.exceptions[location_id]["zip_code"]

            else:
                # City
                city = store["address_display"].split("\n")[-1].split(",")[-2].strip()

                # State
                state = (
                    store["address_display"].split("\n")[-1].split(",")[-1].strip()[:-5]
                )

                # Zip
                zip_code = (
                    store["address_display"].split("\n")[-1].split(",")[-1].strip()[-5:]
                )

            # Street Address
            street_address = (
                store["address"]
                .replace(city, "")
                .replace(state, "")
                .replace(zip_code, "")
                .strip()[:-1]
                .strip()
            )

            # Hours
            hour = store["store_hours"]

            # Lat
            lat = store["latitude"]

            # Lon
            lon = store["longitude"]

            # Phone
            phone = store["phone"]

            # Country
            country = store["country"]

            # Store data
            locations_ids.append(location_id)
            locations_titles.append(location_title)
            street_addresses.append(street_address)
            states.append(state)
            zip_codes.append(zip_code)
            hours.append(hour)
            latitude_list.append(lat)
            longitude_list.append(lon)
            phone_numbers.append(phone)
            cities.append(city)
            countries.append(country)

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

        driver.quit()


scrape = Scraper(URL)
scrape.scrape()
