import json

from Scraper import Scrape
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


URL = "https://www.mayors.com"


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

        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(self.CHROME_DRIVER_PATH, options=options)

        # Fetch stores from location menu
        for num in range(0, 999):
            location_url = f"https://www.mayors.com/store-finder?q=10017&latitude=40.7519846&longitude=-73.96977950000002&page={num}"
            driver.get(location_url)
            result = json.loads(driver.find_element_by_css_selector("pre").text)[
                "results"
            ]
            if result:
                stores.extend(result)
            else:
                break

        for store in stores:
            # Store ID
            location_id = store["name"] if store["name"] != "" else "<MISSING>"

            # Name
            location_title = (
                store["displayName"]
                if store["displayName"].strip() != ""
                else "<MISSING>"
            )

            # Street Address
            street_address = (
                store["address"]["line1"] + store["address"]["line2"]
                if store["address"]["line1"] + store["address"]["line2"] != ""
                else "<MISSING>"
            )

            # City
            city = (
                store["address"]["town"]
                if store["address"]["town"] != ""
                else "<MISSING>"
            )

            # State
            state = (
                store["address"]["region"]["isocodeShort"]
                if store["address"]["region"]["isocodeShort"] != ""
                else "<MISSING>"
            )

            # Zip
            zip_code = (
                store["address"]["postalCode"]
                if store["address"]["postalCode"] != ""
                else "<MISSING>"
            )

            # Hours
            hour = store["openingHours"] if store["openingHours"] else "<MISSING>"

            # Lat
            lat = (
                store["geoPoint"]["latitude"]
                if store["geoPoint"]["latitude"] != ""
                else "<MISSING>"
            )

            # Lon
            lon = (
                store["geoPoint"]["longitude"]
                if store["geoPoint"]["longitude"] != ""
                else "<MISSING>"
            )

            # Phone
            phone = (
                store["address"]["phone"]
                if store["address"]["phone"] != ""
                else "<MISSING>"
            )

            # Country
            country = (
                store["address"]["country"]["isocode"]
                if store["address"]["country"]["isocode"] != ""
                else "<MISSING>"
            )

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
            if "33309" not in zipcode:
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
