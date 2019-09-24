import time
import re

from Scraper import Scrape
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

URL = "https://www.acehotel.com"


class Scraper(Scrape):
    def __init__(self, url):
        Scrape.__init__(self, url)
        self.data = []
        self.block = ['Ace Hotel Kyoto', 'Ace Hotel London Shoreditch']

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
        seen = []

        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(self.CHROME_DRIVER_PATH, options=options)

        driver.get('https://www.acehotel.com/locations/')
        time.sleep(5)

        stores = [link.get_attribute('href') for link in driver.find_elements_by_css_selector('div.v-card__title > a')][:-2]

        for store in stores:
            driver.get(store)
            time.sleep(3)
            if driver.find_element_by_css_selector('title').get_attribute('textContent').split('|')[0].strip() in self.block:
                pass
            else:
                location_info = driver.find_element_by_css_selector('div.hotel-address > span > a').get_attribute('textContent').replace('\n', '').strip()

                # Store ID
                location_id = '<MISSING>'

                # Name
                location_title = driver.find_element_by_css_selector('title').get_attribute('textContent')

                # Type
                location_type = 'Hotel'

                # Street
                street_address = re.search('.+?((?i)street|(?i)broadway|(?i)st|(?i)dr|(?i)avenue)', location_info).group()

                # Country
                country = "US"

                # State
                state = location_info.replace(street_address, '')[1:].split(',')[1].strip()[:-5]

                # city
                city = location_info.replace(street_address, '')[1:].split(',')[0].strip()

                # zip
                zipcode = location_info.replace(street_address, '')[1:].split(',')[1].strip()[-5:]

                # Lat
                lat = '<MISSING>'

                # Long
                lon = '<MISSING>'

                # Phone
                phone = driver.find_element_by_css_selector('div.hotel-phone-email > span > a').get_attribute('textContent')

                # hour
                hour = "Always Open"

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
                location_type,
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
            location_types,
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
