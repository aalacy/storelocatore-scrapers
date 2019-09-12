import json
import requests

from Scraper import Scrape
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


URL = "http://www.thebargainshop.com"


class Scraper(Scrape):
    def __init__(self, url):
        Scrape.__init__(self, url)
        self.data = []
        self.stores_url = []
        self.provinces = []

    def fetch_data(self):
        # store data
        locations_ids = []
        locations_type = []
        locations_titles = []
        street_addresses = []
        cities = []
        states = []
        zip_codes = []
        latitude_list = []
        longitude_list = []
        phone_numbers = []
        hours = []
        stores = []
        countries = []

        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(self.CHROME_DRIVER_PATH, options=options)

        r = requests.get('http://www.thebargainshop.com/ajax_store.cfm?action=provinces')
        self.provinces = [prov['val'] for prov in json.loads(r.content)['data']]

        for prov in self.provinces:
            url = f'http://www.thebargainshop.com/ajax_store.cfm?province={prov}&action=cities'
            r = requests.get(url)
            self.stores_url.extend([url['val'] for url in json.loads(r.content)['data']])

        for store_url in self.stores_url:
            driver.get(f'http://www.thebargainshop.com{store_url}')

            # Location id
            location_id = store_url.replace('/store/', '')[:-1]

            # Location title
            locations_title = driver.find_element_by_id('store_title').text

            # Location type
            location_type = '<MISSING>'

            # Street address
            street_address = driver.find_element_by_id('store_address').text.split(',')[0].strip()

            # City
            city = driver.find_element_by_id('store_address').text.split(',')[1].strip()

            # State
            state = driver.find_element_by_id('store_address').text.split(',')[2].strip()

            # Country
            country = 'CA'

            # Zip code
            zip_code = '<MISSING>'

            # Store hour
            hour = driver.find_element_by_id('store_hours').get_attribute('textContent')

            # Phone
            phone_number = driver.find_element_by_id('store_phone').text

            # Latitude
            lat = '<MISSING>'

            # Longitude
            lon = '<MISSING>'

            locations_ids.append(location_id)
            locations_type.append(location_type)
            locations_titles.append(locations_title)
            street_addresses.append(street_address)
            cities.append(city)
            states.append(state)
            zip_codes.append(zip_code)
            phone_numbers.append(phone_number)
            hours.append(hour)
            countries.append(country)
            latitude_list.append(lat)
            longitude_list.append(lon)


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
                location_type
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
            locations_type
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
