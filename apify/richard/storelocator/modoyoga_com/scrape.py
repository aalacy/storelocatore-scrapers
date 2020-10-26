import re

from Scraper import Scrape
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('modoyoga_com')




URL = "https://modoyoga.com/"


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
        driver.get('https://modoyoga.com/search-results/?userLocation=')
        stores = [card for card in driver.find_elements_by_css_selector('div.row.full-studio-card')]

        for store in stores:
            if store.find_element_by_css_selector('div.contact').get_attribute('innerHTML').split('<br>')[0].split(',')[-1].strip() in ['USA', 'Canada']:
                # Name
                location_title = store.find_element_by_css_selector('div.title').get_attribute('textContent').strip()

                # Page url
                page_url = [url.get_attribute('href') for url in store.find_elements_by_css_selector('a') if url.get_attribute('href')][0]

                # Store ID
                location_id = store.get_attribute('data-studio-id').split('-')[1]

                # Type
                location_type = 'Yoga'

                # Street
                street_address = ' '.join(store.find_element_by_css_selector('div.contact').get_attribute('innerHTML').split('<br>')[0].strip().split(',')[:-3])

                # city
                city = store.find_element_by_css_selector('div.contact').get_attribute('innerHTML').split('<br>')[0].strip().split(',')[-3].strip()

                # State
                state = store.find_element_by_css_selector('div.contact').get_attribute('innerHTML').split('<br>')[0].strip().split(',')[-2].strip()[:2]

                # Phone
                phone = store.find_element_by_css_selector('div.contact').get_attribute('innerHTML').split('<br>')[1].strip()

                # Lat
                lat = '<MISSING>'

                # Long
                lon = '<MISSING>'

                # Country
                country = store.find_element_by_css_selector('div.contact').get_attribute('innerHTML').split('<br>')[0].split(',')[-1].strip()

                # Store data
                states.append(state)
                cities.append(city)
                locations_ids.append(location_id)
                locations_titles.append(location_title)
                street_addresses.append(street_address)
                latitude_list.append(lat)
                longitude_list.append(lon)
                phone_numbers.append(phone)
                countries.append(country)
                location_types.append(location_type)
                page_urls.append(page_url)

        for page_url in page_urls:
            driver.get(page_url)
            logger.info(f'Getting information for {page_url}')

            # zip
            try:
                zipcode = re.search('((?!.*[DFIOQU])[A-VXY][0-9][A-Z] ?[0-9][A-Z][0-9])|([0-9]{5}(?:-[0-9]{4})?)', driver.find_element_by_css_selector('div.col-6.offset-1').get_attribute('innerHTML')).group(0)
            except:
                zipcode = '<MISSING>'

            # hour
            try:
                hour = driver.find_element_by_css_selector('div.row > div.col-6.offset-1 > p:nth-of-type(4)').get_attribute('textContent')
            except:
                hour = '<MISSING>'

            hours.append(hour)
            zip_codes.append(zipcode)

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
