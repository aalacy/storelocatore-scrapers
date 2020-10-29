from Scraper import Scrape
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('apple_com')



URL = "https://www.apple.com/"


class Scraper(Scrape):
    def __init__(self, url):
        Scrape.__init__(self, url)
        self.data = []
        self.exceptions = {
            'https://www.apple.com/retail/appleparkvisitorcenter/': {
                'title': 'Apple Park Visitor Center',
                'street_address': '10600 North Tantau Avenue',
                'city': 'Cupertino',
                'state': 'CA',
                'zipcode': '95014',
                'phone': '(408) 961-1560',
                'hours': """
                Mon - Fri 9:00 a.m. - 7:00 p.m.
                Sat 10:00 a.m. - 7:00 p.m.
                Sun 11:00 a.m. - 6:00 p.m.
                """,
            },
            'https://www.apple.com/retail/carnegielibrary/': {
                'title': 'Apple Carnegie Library',
                'street_address': '801 K Street NW',
                'city': 'Washington',
                'state': 'DC',
                'zipcode': '20001',
                'phone': '(202) 609-6400',
                'hours': """
                Mon - Sat 9:00 a.m. - 9:00 p.m.
                Sun 11:00 a.m. - 7:00 p.m.
                """,
            },
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
        location_types = []
        page_urls = []

        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(self.CHROME_DRIVER_PATH, options=options)

        driver.get('https://www.apple.com/ca/retail/')
        stores = [url.get_attribute('value') for url in driver.find_elements_by_css_selector('div.select-style.select > select > option')[1:]]

        for store in stores:
            logger.info(f'Getting result for {store}')
            driver.get(store)

            # Store ID
            location_id = '<MISSING>'

            # Name
            location_title = self.exceptions[store]['title'] if store in self.exceptions else driver.find_element_by_css_selector('h1.typography-section-headline').text

            # Page url
            page_url = store

            # Type
            location_type = 'Apple Store'

            # Street
            street_address = self.exceptions[store]['street_address'] if store in self.exceptions else driver.find_element_by_css_selector('div.column.large-12.address-store-details').find_element_by_css_selector('p.hcard-address:nth-of-type(1)').text

            # city
            city = self.exceptions[store]['city'] if store in self.exceptions else driver.find_element_by_css_selector('div.column.large-12.address-store-details').find_element_by_css_selector('p.hcard-address:nth-of-type(3)').text.split(',')[0]

            # zip
            zipcode = self.exceptions[store]['zipcode'] if store in self.exceptions else driver.find_element_by_css_selector('div.column.large-12.address-store-details').find_element_by_css_selector('p.hcard-address:nth-of-type(3)').text.split(',')[1][-7:]

            # State
            state = self.exceptions[store]['state'] if store in self.exceptions else driver.find_element_by_css_selector('div.column.large-12.address-store-details').find_element_by_css_selector('p.hcard-address:nth-of-type(3)').text.split(',')[1][:-7].strip()

            # Phone
            phone = self.exceptions[store]['phone'] if store in self.exceptions else driver.find_element_by_css_selector('div.column.large-12.address-store-details').find_element_by_css_selector('p.hcard-address:nth-of-type(4)').text

            # Lat
            lat = '<MISSING>'

            # Long
            lon = '<MISSING>'

            # Hour
            hour = self.exceptions[store]['hours'] if store in self.exceptions else ' '.join([hour.get_attribute('textContent').strip() for hour in driver.find_elements_by_css_selector('div.store-hours')])

            # Country
            country = 'Canada'

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

        driver.get("https://www.apple.com/retail/storelist/")
        stores = [url.get_attribute('href') for url in driver.find_element_by_css_selector('div.column.large-4.medium-12').find_elements_by_css_selector('a')]

        for store in stores:
            logger.info(f'Getting result for {store}')
            driver.get(store)

            # Store ID
            location_id = '<MISSING>'

            # Name
            location_title = self.exceptions[store]['title'] if store in self.exceptions else driver.find_element_by_css_selector('h1.typography-section-headline').text

            # Page url
            page_url = store

            # Type
            location_type = 'Apple Store'

            # Street
            street_address = self.exceptions[store]['street_address'] if store in self.exceptions else driver.find_element_by_css_selector('div.column.large-12.address-store-details').find_element_by_css_selector('p.hcard-address:nth-of-type(1)').text

            # city
            city = self.exceptions[store]['city'] if store in self.exceptions else driver.find_element_by_css_selector('div.column.large-12.address-store-details').find_element_by_css_selector('p.hcard-address:nth-of-type(3)').text.split(',')[0]

            # zip
            zipcode = self.exceptions[store]['zipcode'] if store in self.exceptions else driver.find_element_by_css_selector('div.column.large-12.address-store-details').find_element_by_css_selector('p.hcard-address:nth-of-type(3)').text.split(',')[1][-5:]

            # State
            state = self.exceptions[store]['state'] if store in self.exceptions else driver.find_element_by_css_selector('div.column.large-12.address-store-details').find_element_by_css_selector('p.hcard-address:nth-of-type(3)').text.split(',')[1][:-5].strip()

            # Phone
            phone = self.exceptions[store]['phone'] if store in self.exceptions else driver.find_element_by_css_selector('div.column.large-12.address-store-details').find_element_by_css_selector('p.hcard-address:nth-of-type(4)').text

            # Lat
            lat = '<MISSING>'

            # Long
            lon = '<MISSING>'

            # Hour
            hour = self.exceptions[store]['hours'] if store in self.exceptions else ' '.join([hour.get_attribute('textContent').strip() for hour in driver.find_elements_by_css_selector('div.store-hours')])

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
