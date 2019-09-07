import json

from Scraper import Scrape
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


URL = "https://www.sourceforsports.com"


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
        location_url = "https://www.sourceforsports.com/api/stores/GetStoresLocatorResult?lat=37.5952304&lng=-122.043969&range=10000&rand=8"
        driver.get(location_url)
        stores = json.loads(
            driver.find_element_by_css_selector(
                "div.collapsible-content > span.text"
            ).text
        )["store"]

        for store in stores:
            # Store ID
            location_id = store["StoreId"]

            # Name
            location_title = store["Title"]

            # Type
            location_type = "<MISSING>"

            # Street
            street_address = store["Address"]

            # Country
            country = store["CountryCode"]

            # city
            city = store["City"]

            # zip
            zipcode = store["PostalCode"]

            # Lat
            lat = store["Latitude"]

            # Long
            lon = store["Longitude"]

            # Phone
            phone = store["LocalPhone"]

            driver.get("https://www.sourceforsports.com/en-US/Stores/" + store["Url"])
            state = (
                driver.find_element_by_css_selector("div.address-details > address")
                .get_attribute("innerHTML")
                .split("<br>")[1]
                .strip()
                .split(",")[1]
                .strip()[:2]
            )
            hour_list = driver.find_elements_by_css_selector(
                "ul.open-days.list-unstyled.js-days > li"
            )
            hour = " ".join(
                [hour.get_attribute("textContent").strip() for hour in hour_list]
            )

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
