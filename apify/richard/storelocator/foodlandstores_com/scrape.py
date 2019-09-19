import json

from Scraper import Scrape
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


URL = "http://foodlandstores.com"


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

        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(self.CHROME_DRIVER_PATH, options=options)

        # Fetch store urls from location menu
        location_url = "http://foodlandstores.com/tools/cm?getAll=cities"
        driver.get(location_url)

        stores = json.loads(driver.find_element_by_css_selector("body").text)

        for store in stores:
            # Store ID
            location_id = store["id"] if store["id"] != "" else "<MISSING>"

            # Name
            location_title = (
                store["name"] if store["name"].strip() != "" else "<MISSING>"
            )

            # Street Address
            street_address = (
                store["street"].split("</br>")[0]
                if store["street"].split("</br>")[0] != ""
                else "<MISSING>"
            )

            # City
            city = store["city"] if store["city"] != "" else "<MISSING>"

            # State
            state = store["state"] if store["state"] != "" else "<MISSING>"

            # Zip
            zip_code = store["zip"] if store["zip"] != "" else "<MISSING>"

            # Hours
            hour = store["hours"] if store["hours"] else "<MISSING>"

            # Lat
            lat = store["lat"] if store["lat"] != "" else "<MISSING>"

            # Lon
            lon = store["lng"] if store["lng"] != "" else "<MISSING>"

            # Phone
            phone = store["phone"] if store["phone"] != "" else "<MISSING>"

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
        ):
            self.data.append(
                [
                    self.url,
                    locations_title,
                    street_address,
                    city,
                    state,
                    zipcode,
                    "US",
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
