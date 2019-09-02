from Scrape import Scrape
import json

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


URL = 'https://www.yoshinoyaamerica.com'


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
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(self.CHROME_DRIVER_PATH, options=options)

        # Fetch stores from location menu
        location_url = "https://www.yoshinoyaamerica.com/location/viewer/searchdb.php?lat=37.5952304&lng=-122.043969&value=10000&r=0.4061677943961699"
        driver.get(location_url)
        stores = json.loads(driver.find_element_by_css_selector("pre").text)

        for store in stores:
            # Store ID
            location_id = '<MISSING>'

            # Name
            location_title = store['n'] if store['n'].strip() != '' else '<MISSING>'

            # Street Address
            street_address = store['a'].split(',')[0] if store['a'].split(',')[0] != '' else '<MISSING>'

            # City
            city = store['a'].split(',')[1].strip() if store['a'].split(',')[1].strip() != '' else '<MISSING>'

            # State
            state = store['s'] if store['s'] != '' else '<MISSING>'

            # Zip
            zip_code = store['pc'] if store['pc'] != '' else '<MISSING>'

            # Hours
            hour = store['m1'] if store['m1'] else '<MISSING>'

            # Lat
            lat = store['lat'] if store['lat'] != '' else '<MISSING>'

            # Lon
            lon = store['lng'] if store['lng'] != '' else '<MISSING>'

            # Phone
            phone = store['p'] if 'p' in store.keys() else '<MISSING>'

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
                country
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
            countries
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