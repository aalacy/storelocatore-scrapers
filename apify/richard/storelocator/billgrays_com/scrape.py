import re
import json

from Scraper import Scrape
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

URL = "https://www.billgrays.com/"


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
        driver.get("https://www.billgrays.com/index.cfm?Page=Bill%20Grays%20Locations")
        stores = json.loads([store.get_attribute('innerHTML') for store in driver.find_elements_by_css_selector('script') if store.get_attribute('type') == "application/ld+json"][0])['@graph'][1:]


        for store in stores:
            # Store ID
            location_id = '<MISSING>'

            # Type
            location_type = store['@type']

            # Name
            location_title = store['name']

            # Page url
            page_url = 'https://www.billgrays.com/index.cfm?Page=' + location_title

            # Street
            street_address = store['address']['streetAddress']

            # city
            city = store['address']['addressLocality']

            # zip
            zipcode = store['address']['postalCode']

            # State
            state = store['address']['addressRegion']

            # Phone
            phone = store['address']['telephone']

            # Lat
            lat = re.search('(\-?\d+(\.\d+)?),\s*(\-?\d+(\.\d+)?)', store['hasmap']).group().split(',')[0]

            # Long
            lon = re.search('(\-?\d+(\.\d+)?),\s*(\-?\d+(\.\d+)?)', store['hasmap']).group().split(',')[1]

            # Hour
            hour = ' '.join(store['openingHours'])

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
