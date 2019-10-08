import json
import re

from Scraper import Scrape
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


URL = "https://www.porsche.com"


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

        location_url = "https://www.porsche.com/all/dealer2/canada/externalSearchJson.aspx?geo=49.2827291%7C-123.12073750000002&lim=1000"
        driver.get(location_url)
        stores.extend(
            json.loads(driver.find_element_by_css_selector("pre").text)["dealers"][
                "dealer"
            ]
        )

        for store in stores:
            # Store ID
            location_id = store["id"]

            # Name
            location_title = store["name"]

            # Type
            location_type = "<MISSING>"

            # Street
            street_address = store["address"][0]["street"]

            # State
            state = store["address"][0]["region"]

            # city
            city = store["address"][0]["city"]

            # zip
            zipcode = store["address"][0]["postalCode"]

            # Lat
            lat = "<MISSING>"

            # Long
            lon = "<MISSING>"

            # Phone
            phone = store["address"][0]["phone"]

            # Hour
            hour = store["details"]["main"]["hours"]
            if location_title.strip() == 'Porsche Bellingham':
                hour = "Monday - Friday : 8:30AM - 7:00PM, Saturday : 9:00AM - 6:00PM"

            # Country
            if re.match("^(\d{5})?$", zipcode.strip()):
                country = "US"
            elif re.match("[A-Z][0-9][A-Z]\s[0-9][A-Z][0-9]", zipcode.strip()):
                country = "CA"
            else:
                country = "<MISSING>"

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
            if country == "<MISSING>":
                pass
            else:
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
