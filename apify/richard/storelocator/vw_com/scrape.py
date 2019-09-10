import json

import sgzip
from Scraper import Scrape
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


URL = "https://www.vw.com"


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
        dealers = []
        seen = []

        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(self.CHROME_DRIVER_PATH, options=options)

        # Fetch stores from location menu
        for zip_search in sgzip.for_radius(50):
            location_url = (
                f"https://www.vw.com/vwsdl/rest/product/dealers/zip/{zip_search}.json"
            )
            driver.get(location_url)
            dealers.extend(
                json.loads(driver.find_element_by_css_selector("pre").text)["dealers"]
            )

        for dealer in dealers:
            # Store ID
            location_id = dealer["dealerid"]

            # Name
            location_title = dealer["name"]

            # Street
            street_address = (dealer["address1"] + " " + dealer["address2"]).strip()

            # Country
            country = dealer["country"]

            # State
            state = dealer["state"]

            # city
            city = dealer["city"]

            # zip
            zipcode = dealer["postalcode"]

            # Lat
            lat = dealer["latlong"].split(",")[0]

            # Long
            lon = dealer["latlong"].split(",")[1]

            # Phone
            phone = dealer["phone"]

            # hour
            hour = dealer["hours"]

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

        driver.quit()


scrape = Scraper(URL)
scrape.scrape()
