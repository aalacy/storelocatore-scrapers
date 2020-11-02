import json

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from Scraper import Scrape


URL = "https://suddenserviceonline.com/"


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
        page_urls = []
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(self.CHROME_DRIVER_PATH, options=options)

        # Fetch stores
        location_url = "https://suddenserviceonline.com/locations/"
        driver.get(location_url)
        stores = driver.find_element_by_id('gmwd_container_1').find_element_by_css_selector('script').get_attribute('innerHTML')
        stores = json.loads(stores.split('= JSON.parse(')[1].split('\n')[0][1:-3])

        for id in stores.keys():
            store = stores[id]

            # Store ID
            location_id = store['id']

            # Page url
            page_url = '<MISSING>'

            # Type
            location_type = 'Convenience Store'

            # Name
            location_title = store['title']

            # Street
            street_address = store['address'].split(',')[0]

            # city
            city = store['address'].split(',')[1]

            # zip
            zipcode = '<MISSING>'

            # State
            state = store['address'].split(',')[2]

            # Phone
            phone = '<MISSING>'

            # Lat
            lat = store['lat']

            # Long
            lon = store['lng']

            # Hour
            hour = '24 Hour'

            # Country
            country = store['address'].split(',')[3]

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


scrape = Scraper(URL)
scrape.scrape()
