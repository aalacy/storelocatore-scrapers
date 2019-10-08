import sgzip
import json

from Scraper import Scrape
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


URL = "https://www.stinehome.com"


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

        for zipcode_search in sgzip.for_radius(100):
            location_url = f'https://www.stinehome.com/on/demandware.store/Sites-Stine-Site/en_US/Stores-FindStores?showMap=true&radius=100&postalCode={zipcode_search}'
            driver.get(location_url)
            stores.extend(json.loads(driver.find_element_by_css_selector('pre').text)['stores'])

        for store in stores:
            # Store ID
            location_id = store['ID']

            # Name
            location_title = store['name']

            # Street Address
            street_address = store['address1'] + ' ' + store['address2'] if store['address2'] else store['address1']

            # City
            city = store['city']

            # State
            state = store['stateCode']

            # Zip
            zip_code = store['postalCode']

            # Hours
            hour = store['storeHours']

            # Lat
            lat = store['latitude']

            # Lon
            lon = store['longitude']

            # Phone
            phone = store['phone']

            # Country
            country = store['countryCode']

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
