import requests

from Scraper import Scrape
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('mysagedental_com')




URL = "https://mysagedental.com/"


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

        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(self.CHROME_DRIVER_PATH, options=options)

        headers = {
            'Sec-Fetch-Mode': 'cors',
            'Referer': 'https://mysagedental.com/find-locations/',
            'DNT': '1',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36',
        }

        stores = requests.get('https://mysagedental.com/wp-content/themes/sharkbite-child/assets/js/google-maps-json.php', headers=headers).json()['features']


        for store in stores:
            # Store ID
            location_id = '<MISSING>'

            # Page url
            page_url = store['properties']['locpage']
            logger.info(f"Now scraping {page_url}")

            # Type
            location_type = store['properties']['category']

            # Name
            location_title = store['properties']['name']

            # Street
            street_address = store['properties']['address1'] + store['properties']['address2']

            # city
            city = store['properties']['city']

            # zip
            zipcode = store['properties']['zip']

            # State
            state = store['properties']['state']

            # Phone
            phone = store['properties']['phone']

            # Lat
            lat = store['geometry']['coordinates'][1]

            # Long
            lon = store['geometry']['coordinates'][0]

            # Hour
            driver.get(page_url)
            hour = driver.find_element_by_css_selector('div.locHours').get_attribute('textContent').strip().replace('\n', '').replace('\t', '')

            # Country
            country = 'US'

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

        driver.quit()


scrape = Scraper(URL)
scrape.scrape()
