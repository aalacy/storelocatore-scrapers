import re

from Scraper import Scrape
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

URL = "http://www.pitstopc-stores.com/"


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
        driver.get("http://www.pitstopc-stores.com/practice-areas.html")
        stores = ' '.join([store.get_attribute('innerHTML').replace('(Empire Eatery)', '').replace('(Laundromat)', '').replace('(Pit Stop Deli)', '') for store in driver.find_elements_by_css_selector('div.txt > p > span > strong')]).replace('&nbsp;', ' ').replace('<br> North Rose', '<br><br>North Rose').split('<br><br>')

        for store in stores:
            store = store.strip('<br>').split('<br>')

            # Store ID
            location_id = '<MISSING>'

            # Name
            location_title = store[0]

            # Page url
            page_url = '<MISSING>'

            # Type
            location_type = 'Gas Station'

            # Street
            street_address = store[1].split(',')[0]

            # city
            city = store[0].split(',')[0]

            # zip
            zipcode = re.search('[0-9]{5}(?:-[0-9]{4})?', store[1]).group(0)

            # State
            state = store[0].split(',')[1]

            # Phone
            phone = store[2]

            # Lat
            lat = '<MISSING>'

            # Long
            lon = '<MISSING>'

            # Hour
            hour = '24 Hours'

            # Country
            country = 'US'

            # Store data
            locations_ids.append(location_id)
            page_urls.append(page_url)
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
