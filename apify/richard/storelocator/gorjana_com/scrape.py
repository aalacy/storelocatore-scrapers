import json
import re

from Scraper import Scrape
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


URL = "https://www.gorjana.com/"


class Scraper(Scrape):
    def __init__(self, url):
        Scrape.__init__(self, url)
        self.data = []
        self.seen = []

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
        page_urls = []

        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(self.CHROME_DRIVER_PATH, options=options)

        location_url = 'https://gorjana.com/pages/store-locator'
        driver.get(location_url)
        stores = [info.get_attribute('innerHTML') for info in driver.find_elements_by_css_selector('script') if info.get_attribute('type') == 'text/javascript']
        stores = stores[-12].replace('var storeMarkers = ', '').strip().split('\n')
        new_stores = []
        for store_info in stores:
            if re.match('^[a-zA-Z]', store_info.strip()):
                new_stores.append(
                    '"' + store_info.strip().replace(':', '":')
                )
            else:
                new_stores.append(store_info)

        stores = json.loads('\n'.join(new_stores))
        for store in stores:
            # Store ID
            location_id = store['id']

            # Page url
            page_url = '<MISSING>'

            # Type
            location_type = 'Luxury Shop'

            # Name
            location_title = store['title']

            # Street
            street_address = store['address'].replace('<br />', ', ').split(',')[0]

            # city
            city = store['address'].replace('<br />', ', ').split(',')[-2]

            # zip
            zipcode = store['address'].replace('<br />', ', ').split(',')[-1][-5:]

            # State
            state = store['address'].replace('<br />', ', ').split(',')[-1][:-5].strip()

            # Phone
            phone = store['phone']

            # Lat
            lat = '<MISSING>'

            # Long
            lon = '<MISSING>'

            # Hour
            hour = store['working_hours']

            # Country
            country = 'US'

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
            page_urls.append(page_url)

        for (
                locations_title,
                page_url,
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
            page_urls,
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
                    page_url,
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