from Scrape import Scrape
import json

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait


URL = 'https://www.stinehome.com'


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
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(self.CHROME_DRIVER_PATH, options=options)

        location_url = "https://www.stinehome.com/stores?showMap=false"
        driver.get(location_url)
        stores.extend(driver.find_elements_by_css_selector('div.store-name > a'))
        store_urls = [store.get_attribute('href') for store in stores]

        for store_url in store_urls:
            driver.get(store_url)

            # Wait until element appears - 10 secs max
            wait = WebDriverWait(driver, 10)
            wait.until(ec.visibility_of_element_located((By.CSS_SELECTOR, "body")))

            # Store ID
            location_id = driver.find_element_by_css_selector('h1.page-title').get_attribute('id')

            # Location Title
            location_title = driver.find_element_by_css_selector('h1.page-title').text

            # Address
            street_address = driver.find_element_by_css_selector('div.col-3 > address > p').get_attribute('innerHTML').split('<br>')[0].strip()

            # City
            city = driver.find_element_by_css_selector('div.col-3 > address > p').get_attribute('innerHTML').split('<br>')[1].strip().split(',')[0].strip()

            # State
            state = driver.find_element_by_css_selector('div.col-3 > address > p').get_attribute('innerHTML').split('<br>')[1].strip().split(',')[1][:3].strip()

            # Zip
            zipcode = driver.find_element_by_css_selector('div.col-3 > address > p').get_attribute('innerHTML').split('<br>')[1].strip().split(',')[1][3:].strip()

            # Phone
            phone = driver.find_element_by_css_selector('a.storelocator-phone').text

            # Hours
            hour = driver.find_element_by_css_selector('div.store-hours').text

            # Lat
            lat = json.loads(driver.find_element_by_css_selector('div.jumbotron.map-canvas').get_attribute('data-locations'))[0]['latitude']

            # Long
            lon = json.loads(driver.find_element_by_css_selector('div.jumbotron.map-canvas').get_attribute('data-locations'))[0]['longitude']

            # Type
            location_type = '<MISSING>'

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
            location_types
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