import sgzip
import json

from Scraper import Scrape
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('mattressfirm_com')



URL = "https://www.mattressfirm.com/"


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
        stores = []

        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(self.CHROME_DRIVER_PATH, options=options)

        for zip_search in sgzip.for_radius(50):
            driver.get(f"https://www.mattressfirm.com/stores/search?q={zip_search}")
            data = [loc.find_element_by_css_selector('a.gaq-link').get_attribute('href') for loc in driver.find_elements_by_css_selector('div.map-list-item-wrap')]
            stores.extend(data)
            logger.info(f"{len(data)} locations scraped for {zip_search}")

        for store_url in stores:
            if store_url not in self.seen:
                driver.get(store_url)
                store = json.loads([file.get_attribute('textContent') for file in driver.find_elements_by_css_selector('script') if file.get_attribute('type') == 'application/ld+json'][0])[0]

                # Store ID
                location_id = store['url'].split('/')[-1].replace('.html', '').split('-')[-1]

                # Name
                location_title = store['name']

                # Page url
                page_url = store['url']

                # Type
                location_type = 'Retail'

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
                lat = store['geo']['latitude']

                # Long
                lon = store['geo']['longitude']

                # Hour
                hour = store['openingHours']

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
                self.seen.append(store_url)

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
