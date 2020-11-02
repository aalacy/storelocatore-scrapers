import json
import sgzip

from Scraper import Scrape
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('examone_com')



URL = "https://www.examone.com/"


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
        stores = []
        page_urls = []

        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(self.CHROME_DRIVER_PATH, options=options)
        for zipcode_search in sgzip.for_radius(100):
            driver.get(f'https://www.examone.com/locations/?zipInput={zipcode_search}&dist=100&submit=find+locations')
            data = driver.find_elements_by_css_selector('script')[-2]
            data = json.loads(data.get_attribute('innerHTML').replace('/* <![CDATA[ */', '').replace('/* ]]> */', '').replace('var php_vars = "', '').replace('\\', '').strip()[:-2])
            stores.extend(data)
            logger.info(f"{len(data)} stores scraped for {zipcode_search}.")

        for store in stores:
            if store['qsl_id'] not in self.seen:
                # Store ID
                location_id = store['qsl_id']

                # Page url
                page_url = '<MISSING>'

                # Type
                location_type = 'Pawn Shop'

                # Name
                location_title = f"Exam One - {store['qsl_city']}"

                # Street
                street_address = store['qsl_address'] + ' ' + store['qsl_address2']

                # city
                city = store['qsl_city']

                # zip
                zipcode = store['qsl_zip']

                # State
                state = store['qsl_state']

                # Phone
                phone = store['qsl_phone']

                # Lat
                lat = store['qsl_latitude']

                # Long
                lon = store['qsl_longitude']

                # Hour
                hour = store['qsl_hours'] if store['qsl_hours'] else '<MISSING>'

                # Country
                country = store['qsl_country']

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
                self.seen.append(store['qsl_id'])

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
