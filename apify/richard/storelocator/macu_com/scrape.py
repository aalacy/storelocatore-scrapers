from Scrape import Scrape
import json

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


URL = 'https://www.macu.com'


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

        # Fetch stores from location menu
        page = 1
        while True:
            location_url = f"https://www.macu.com/Handlers/branchlocatorhandler.ashx?lat=40.7607793&lng=-111.89104739999999&pageNum={page}&radius=10000000&type=1"
            driver.get(location_url)
            branches = driver.find_element_by_css_selector('pre').text
            branch_list = json.loads(branches)
            if len(branch_list) > 0:
                stores.extend(branch_list)
            else:
                break
            page += 1

        for store in stores:
            # Store ID
            location_id = store['Id']

            # Name
            location_title = store['Name']

            # Type
            location_type = '<MISSING>'

            # Street
            street_address = (store['Address']['Address1'] + ' ' + (store['Address']['Address2'] if store['Address']['Address2'] else '')).strip()

            # Country
            country = 'US'

            # State
            state = store['Address']['City']

            # city
            city = store['State']

            # zip
            zipcode = store['Address']['Zip']

            # Lat
            lat = store['Address']['Latitude']

            # Long
            lon = store['Address']['Longitude']

            # Phone
            phone = store['Phone']

            # hour
            hour = store['Hours']

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