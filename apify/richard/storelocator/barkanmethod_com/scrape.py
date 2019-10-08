import re

from Scraper import Scrape
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


URL = "barkanmethod.com"


class Scraper(Scrape):
    def __init__(self, url):
        Scrape.__init__(self, url)
        self.data = []
        self.locations = [
            'https://www.barkanmethod.com/location-boca-raton/',
            'https://www.barkanmethod.com/location-ft-lauderdale/'
        ]

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

        for store in self.locations:
            driver.get(store)

            location_info = driver.find_element_by_css_selector('div.content > p:nth-of-type(1)').text.split('\n') + driver.find_element_by_css_selector('div.content > p:nth-of-type(2)').text.split('\n')

            location_link = [p.get_attribute('href') for p in driver.find_elements_by_css_selector('div.content > p > a')]

            for link in location_link:
                if 'https://www.google.com/maps?' in link:
                    google_link = link
                    break

            # Store ID
            location_id = '<MISSING>'

            # Name
            location_title = driver.find_element_by_css_selector('h2.h2').text.replace('Location', '').strip()

            # City
            city = driver.find_element_by_css_selector('h2.h2').text.replace('Location', '').strip()

            # Street Address
            street_address = location_info[1]

            # State
            state = 'FL'

            # Zip
            zip_code = location_info[2][-5:]

            # Hours
            hour = '<MISSING>'

            ll_match = re.search('([-+]?)([\d]{1,2})(((\.)(\d+)(,)))(\s*)(([-+]?)([\d]{1,3})((\.)(\d+))?)', google_link)

            # Lat
            lat = ll_match.group().split(',')[0] if ll_match else '<MISSING>'

            # Lon
            lon = ll_match.group().split(',')[1] if ll_match else '<MISSING>'

            # Phone
            phone = location_info[0]

            # Country
            country = "US"

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
