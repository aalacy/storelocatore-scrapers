import json

from Scraper import Scrape
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


URL = "https://www.economical.com"


class Scraper(Scrape):
    def __init__(self, url):
        Scrape.__init__(self, url)
        self.data = []
        self.seen = []
        self.postal_codes = []

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

        for first in "ABCEGHJKLMNPRSTVXY".lower():
            for second in range(0, 10):
                for third in "ABCEGHJKLMNPRSTVWXYZ".lower():
                    self.postal_codes.append(first + str(second) + third + "0a0")

        for postal in self.postal_codes:
            for page in range(1, 11):
                print(f"Now combing page {page} for {postal.upper()}")
                location_url = f"https://www.economical.com/ecocom/broker/search/{postal}/100/{page}"
                driver.get(location_url)
                if (
                    len(
                        json.loads(
                            driver.find_element_by_css_selector("body > pre").text
                        )["items"]
                    )
                    > 0
                ):
                    stores.extend(
                        json.loads(
                            driver.find_element_by_css_selector("body > pre").text
                        )["items"]
                    )
                else:
                    break
            print(f"The length of brokers is now: {len(stores)}")

        for store in stores:
            if store["brokeragenme"] not in self.seen:
                # Store ID
                location_id = "<MISSING>"

                # Name
                location_title = store["brokeragenme"]

                # Street Address
                street_address = store["brokeraddr"]

                # City
                city = store["cityNme"]

                # State
                state = store["provinceNme"]

                # Phone
                phone = store["phoneNum"]

                # Hours
                hour = "<MISSING>"

                # Lat
                lat = store["Latitude"]

                # Lon
                lon = store["Longitude"]

                # Country
                country = "CA"

                # Zip
                zip_code = store["postalCd"]

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

                self.seen.append(store["brokeragenme"])

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
