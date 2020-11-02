import sgzip

from Scraper import Scrape
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('finishline_com')



URL = "https://www.finishline.com/"


class Scraper(Scrape):
    def __init__(self, url):
        Scrape.__init__(self, url)
        self.data = []
        self.seen = []

    def fetch_data(self):
        # store data
        search = sgzip.ClosestNSearch()
        search.initialize()
        zip_search = search.next_zip()

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

        while zip_search:
            driver.get(f"https://stores.finishline.com/search.html?q={zip_search}")
            data = [loc.get_attribute('href') for loc in driver.find_elements_by_css_selector('a.location-card-link.location-card-link-page')]
            stores.extend(data)
            logger.info(f"{len(data)} locations scraped for {zip_search}")
            zip_search = search.next_zip()

        for store in stores:
            if store not in self.seen:
                driver.get(store)

                # Store ID
                location_id = '<MISSING>'

                # Name
                location_title = driver.find_element_by_css_selector('span.location-name-geo').get_attribute('textContent')

                # Page url
                page_url = store

                # Type
                location_type = 'Retail'

                # Street
                street_address = driver.find_element_by_css_selector('span.c-address-street-1').get_attribute('textContent')

                # city
                city = driver.find_element_by_css_selector('span.c-address-city > span').get_attribute('textContent')

                # zip
                zipcode = driver.find_element_by_css_selector('span.c-address-postal-code').get_attribute('textContent')

                # State
                state = driver.find_element_by_css_selector('abbr.c-address-state').get_attribute('textContent')

                # Phone
                phone = driver.find_element_by_css_selector('span.c-phone-number-span.c-phone-main-number-span').get_attribute('textContent')

                # Lat
                lat = '<MISSING>'

                # Long
                lon = '<MISSING>'

                # Hour
                hour = driver.find_element_by_css_selector('table.c-location-hours-details').get_attribute('textContent')

                # Country
                country = driver.find_element_by_css_selector('abbr.c-address-country-name').get_attribute('textContent')

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
                self.seen.append(store)

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
