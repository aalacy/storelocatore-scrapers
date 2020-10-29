from Scraper import Scrape
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('unitedoilco_com')



URL = "http://www.unitedoilco.com/"


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
        driver.get("http://www.unitedoilco.com/locations?brand=foodmart")
        stores = [url.get_attribute('href') for url in driver.find_element_by_css_selector('table.list-of-station > tbody').find_elements_by_css_selector('a')]

        for store in stores:
            logger.info(f"Scraping: {store}")
            driver.get(store)

            # Store ID
            location_id = store.replace('http://www.unitedoilco.com/station?IDS=', '')

            # Page url
            page_url = store

            # Type
            location_type = 'Gas Station'

            # Street
            address_info = driver.find_element_by_id('content').find_element_by_css_selector('div:nth-of-type(2) > h2').get_attribute('innerHTML').split('<br>')
            street_address = ' '.join(address_info[:-1])

            # city
            city = address_info[-1].split(',')[0]

            # zip
            zipcode = address_info[-1].split(',')[1][-5:]

            # State
            state = address_info[-1].split(',')[1][:-5].strip()

            # Name
            location_title = f'United Oil - {city}'

            # Phone
            phone = driver.find_element_by_id('content').find_element_by_css_selector('div:nth-of-type(2) > h1').get_attribute('textContent')

            # Lat
            lat = '<MISSING>'

            # Long
            lon = '<MISSING>'

            # Hour
            hour = 'Always Open'

            # Country
            country = 'USA'

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
