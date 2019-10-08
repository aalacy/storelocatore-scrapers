import time
import re

from Scraper import Scrape
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


URL = "https://www.swatch.com"


class Scraper(Scrape):
    def __init__(self, url):
        Scrape.__init__(self, url)
        self.data = []
        self.countries_search = ['Canada', 'United+States']
        self.patterns = {
            'us_pattern': '\d{5}\s',
            'ca_pattern': '[A-Z][0-9][A-Z]\s[0-9][A-Z][0-9]'
        }

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

        for country_search in self.countries_search:
            location_url = f'https://www.swatch.com/en_us/store-locator#q={country_search}'
            driver.get(location_url)
            time.sleep(10)
            stores.extend([store.get_attribute('href') for store in driver.find_elements_by_css_selector('div.store.vcard > div.storeInfo > div.buttons > a')])

        for store in stores:
            driver.get(store)

            # Store ID
            location_id = '<MISSING>'

            # Name
            location_title = driver.find_element_by_css_selector('header.main > h1').text

            # Street Address
            location_info = driver.find_element_by_css_selector('address > span:nth-of-type(2)').get_attribute('textContent').strip().split('\n')
            street_address = location_info[0]

            # City
            city = re.search('([A-Za-z]+)\s?([A-Za-z]+)\s?([A-Za-z]+),\s([A-Za-z]+)\s?([A-Za-z]+)', re.sub('.+?(?=[0-9])', '', location_info[1])).group().split(', ')[0] if re.search('([A-Za-z]+)\s?([A-Za-z]+)\s?([A-Za-z]+),\s([A-Za-z]+)\s?([A-Za-z]+)', re.sub('.+?(?=[0-9])', '', location_info[1])) else '<MISSING>'

            # State
            state = re.search('([A-Za-z]+)\s?([A-Za-z]+)\s?([A-Za-z]+),\s([A-Za-z]+)\s?([A-Za-z]+)', re.sub('.+?(?=[0-9])', '', location_info[1])).group().split(', ')[1] if re.search('([A-Za-z]+)\s?([A-Za-z]+)\s?([A-Za-z]+),\s([A-Za-z]+)\s?([A-Za-z]+)', re.sub('.+?(?=[0-9])', '', location_info[1])) else '<MISSING>'

            # Phone
            try:
                phone = driver.find_element_by_css_selector('span.phone').text
            except:
                phone = '<MISSING>'

            # Hours
            try:
                hour = driver.find_element_by_css_selector('div.opening > span.table').get_attribute('textContent')
            except:
                hour = '<MISSING>'

            long_lat = driver.find_element_by_css_selector('a.button.expand.getDirections').get_attribute('href')
            long_lat = re.search('(\-?\d+(\.\d+)?),\s*(\-?\d+(\.\d+)?)', long_lat).group().split(',')

            # Lat
            lat = long_lat[0]

            # Lon
            lon = long_lat[1]

            # Country
            country = 'US' if 'united-states' in store else 'CA'

            # Zip
            if country == 'US':
                if re.search(self.patterns['us_pattern'], location_info[1]):
                    zip_code = re.search(self.patterns['us_pattern'], location_info[1]).group()
                else:
                    zip_code = '<MISSING>'
            else:
                if re.search(self.patterns['us_pattern'], location_info[1]):
                    zip_code = re.search(self.patterns['ca_pattern'], location_info[1]).group()
                else:
                    zip_code = '<MISSING>'


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
