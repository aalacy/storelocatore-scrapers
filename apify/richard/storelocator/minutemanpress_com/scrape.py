import re

from Scraper import Scrape
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('minutemanpress_com')




URL = "https://www.minutemanpress.com/"


class Scraper(Scrape):
    def __init__(self, url):
        Scrape.__init__(self, url)
        self.data = []
        self.seen = [
            'http://www.citycenter.minutemanpress.com/',
            'http://www.allentownpa.minutemanpress.com/',
            'http://www.bethlehempa.minutemanpress.com/',
            'http://www.conroe.minutemanpress.com/'
        ]
        self.exceptions = {
            "http://www.brentwood.minutemanpress.com/": {
                'address': '1905 Conta Costa Blvd.',
                'city': 'Pleasant Hill',
                'state': 'CA',
                'zipcode': '94523'
            },
            "http://www.impressaz.com/": {
                'address': '14525 N. 79th Street, Suite E.',
                'city': 'Scottsdale',
                'state': 'AZ',
                'zipcode': '85260'
            },
            "http://brampton11.minutemanpress.ca/": {
                'address': '211 Wilkinson Road Unit 4',
                'city': 'Brampton',
                'state': 'Ontario',
                'zipcode': 'L6T 4M2'
            },
            "http://www.mrpm.minutemanpress.com/": {
                'address': '#6-22935 Lougheed Hwy',
                'city': 'Maple Ridge',
                'state': 'BC',
                'zipcode': 'V2X 2W1'
            },
            "http://www.edmonton13.minutemanpress.ca/": {
                'address': '4752 76 Ave NW',
                'city': 'Edmonton',
                'state': 'AB',
                'zipcode': 'T6B 0A5'
            },
            "http://www.alabaster.minutemanpress.com/": {
                'address': '2659 Pelham Parkway',
                'city': 'Pelham',
                'state': 'AL',
                'zipcode': '35124'
            },
            "http://www.minutemancl.com/": {
                'address': '835 Virginia Road Ste G',
                'city': 'Crystal Lake',
                'state': 'IL',
                'zipcode': '60014'
            },
            "http://www.minutemanbeverly.com/": {
                'address': '409 Cabot Street',
                'city': 'Beverly',
                'state': 'MA',
                'zipcode': '01915'
            },
            "http://www.minutemanlex.com/": {
                'address': '2408 Merchant Street',
                'city': 'Lexington',
                'state': 'KY',
                'zipcode': '40511'
            },
            "http://www.br.minutemanpress.com/": {
                'address': '15110 Market Street, Suite B',
                'city': 'Baton Rouge',
                'state': 'LA',
                'zipcode': '70817'
            },
            "http://www.fallriver.minutemanpress.com/": {
                'address': '435 Columbia St.',
                'city': 'Fall River',
                'state': 'MA',
                'zipcode': '02721'
            },
            "http://www.mmpressfitchburg.com/": {
                'address': '386 Summer Street',
                'city': 'Fitchburg',
                'state': 'MA',
                'zipcode': '01420'
            },
            "http://www.portland24-or.minutemanpress.com/": {
                'address': '1308 SW 2nd Ave.',
                'city': 'Portland',
                'state': 'OR',
                'zipcode': '97201'
            },
            "http://www.arlingtontx.minutemanpress.com/": {
                'address': '801 Ave H E Suite 100',
                'city': 'Arlington',
                'state': 'TX',
                'zipcode': '76011'
            },
            "http://www.fredericksburg.minutemanpress.com/": {
                'address': '10699 Courthouse Rd.',
                'city': 'Fredericksburg',
                'state': 'VA',
                'zipcode': '22407'
            },
            "http://www.southcharleston.minutemanpress.com/": {
                'address': '503 D Street So.',
                'city': 'Charleston',
                'state': 'WV',
                'zipcode': '25303'
            },
        }

    def fetch_data(self):
        # store data
        locations_ids = []
        locations_titles = []
        street_addresses = []
        cities = []
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

        for search_country in ['ca', 'us']:
            stores = []
            prov_state = 'provinces' if search_country == 'ca' else 'states'
            logger.info(f"Getting {prov_state} for {search_country.upper()}")
            driver.get(f'https://www.minutemanpress.com/locations/locations.html/{search_country}')
            states = [url.get_attribute('action') for url in driver.find_elements_by_css_selector('div.mmp-corp-store-search-filter-options > form')]
            for state in states:
                logger.info(f"Getting stores for state website: {state}")
                driver.get(state)
                stores.extend([store_url.get_attribute('href') for store_url in driver.find_elements_by_css_selector('a.visit-website.button')])

            logger.info("\n Preparing for scrape each store. \n")

            for store in stores:
                if store not in self.seen:
                    logger.info(f"Getting url for {store}")
                    driver.get(store)

                    try:
                        # Store ID
                        location_id = '<MISSING>'

                        # Page url
                        page_url = store

                        # Type
                        location_type = 'Print Center'

                        # Street
                        address_info = [re.sub('(Canada)|(United States)|\((.*?)\)', '', address.get_attribute('textContent')).replace('\t', '').replace('\n', '').strip() for address in driver.find_element_by_css_selector('div.location__address').find_elements_by_css_selector('div') if address.get_attribute('itemprop') == 'streetAddress']
                        address_info = [info for info in address_info if info != '' and not re.match('(.*)@(.*).(.*)', info)]
                        street_address = ' '.join(address_info[:-1]) if store not in self.exceptions.keys() else self.exceptions[store]['address']

                        # zip
                        zipcode = self.exceptions[store]['zipcode'] if store in self.exceptions.keys() else (address_info[-1].strip().split(' ')[-1] if search_country == 'us' else address_info[-1][-7:].strip())

                        # city
                        city = address_info[-1].replace(zipcode, '').split(',')[0].strip() if store not in self.exceptions.keys() else self.exceptions[store]['city']

                        # Name
                        location_title = f"Minute man press - {city}"

                        # State
                        state = address_info[-1].replace(zipcode, '').split(',')[-1].strip() if store not in self.exceptions.keys() else self.exceptions[store]['state']

                        # Phone
                        phone = driver.find_element_by_css_selector('div.location-phone.location-phone--1 > span.value > a').get_attribute('textContent')

                        # Lat
                        lat = '<MISSING>'

                        # Long
                        lon = '<MISSING>'

                        # Hour
                        try:
                            hour = driver.find_element_by_css_selector('div.location__hours').get_attribute('textContent').replace('\n', '').replace('\t', '').strip()
                        except:
                            hour = '<MISSING>'

                        # Country
                        country = search_country.upper()

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
                    except:
                        logger.info(f"{store} is not scrapable")
                        pass

            logger.info(f"Done scraping stores for {search_country.upper()}")

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
                    self.url.strip(),
                    page_url.strip(),
                    locations_title.strip(),
                    street_address.strip(),
                    city.strip(),
                    state.strip(),
                    zipcode.strip(),
                    country.strip(),
                    location_id.strip(),
                    phone_number.strip(),
                    location_type.strip(),
                    latitude.strip(),
                    longitude.strip(),
                    hour.strip(),
                ]
            )

        driver.quit()


scrape = Scraper(URL)
scrape.scrape()
