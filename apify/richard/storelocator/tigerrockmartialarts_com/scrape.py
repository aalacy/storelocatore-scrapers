import json
import sgzip

from Scraper import Scrape
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


URL = "https://tigerrockmartialarts.com"


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

        for zip_search in sgzip.for_radius(100):
            driver.get(f'https://tigerrockmartialarts.com/?geolocate={zip_search}&radius=100')
            result = json.loads(driver.find_element_by_css_selector('body').text)['locations'] if 'locations' in json.loads(driver.find_element_by_css_selector('body').text).keys() else []
            stores.extend(result)

        for store in stores:
            # Store ID
            location_id = store['location_id']

            # Name
            location_title = store['name']

            # Street Address
            street_address = store['location_address']

            # City
            city = store['location_city']

            # State
            state = store['location_state']

            # Zip
            zip_code = store['location_zip']

            # Hours
            hour = '<MISSING>'

            # Lat
            lat = store['lat']

            # Lon
            lon = store['lng']

            # Phone
            phone = store['location_phone']

            # Country
            country = 'US'

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
