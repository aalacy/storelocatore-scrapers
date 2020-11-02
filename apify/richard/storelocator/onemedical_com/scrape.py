import re

from Scraper import Scrape
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


URL = "https://www.onemedical.com/"


class Scraper(Scrape):
    def __init__(self, url):
        Scrape.__init__(self, url)
        self.data = []
        self.stores_url = []
        self.provinces = []
        self.coords = []

    def fetch_data(self):
        # store data
        locations_ids = []
        locations_type = []
        locations_titles = []
        street_addresses = []
        cities = []
        states = []
        zip_codes = []
        latitude_list = []
        longitude_list = []
        phone_numbers = []
        hours = []
        stores = []
        countries = []

        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(self.CHROME_DRIVER_PATH, options=options)

        driver.get('https://www.onemedical.com/locations/')
        states_list = [url.get_attribute('href') for url in driver.find_elements_by_css_selector('div.link-list.link-list--locations > ul > li > a')]

        for state in states_list:
            driver.get(state)

            if 'office-list' in driver.find_element_by_css_selector('body').get_attribute('innerHTML'):
                stores.extend([url.get_attribute('href') for url in driver.find_elements_by_css_selector('a.office-list__anchor')])

        for store in stores:
            driver.get(store)

            # Location id
            location_id = '<MISSING>'

            # Location title
            locations_title = driver.find_element_by_css_selector('h1.page-hero__headline').text.strip()

            # Street
            street_address = ' '.join([address.text for address in driver.find_elements_by_css_selector('div.office-info__information > p') if address.get_attribute('itemprop') == 'streetAddress'])

            # City
            city = driver.find_element_by_css_selector('div.office-info__information > span:nth-of-type(1)').text

            # Sttate
            state = driver.find_element_by_css_selector('div.office-info__information > span:nth-of-type(2)').text

            # Zip
            zip_code = driver.find_element_by_css_selector('div.office-info__information > span:nth-of-type(3)').text

            # Phone
            phone_number = [info.text for info in driver.find_elements_by_css_selector('div.office-info__information > p') if info.get_attribute('itemprop') == 'telephone'][0]

            # Hour
            hour = driver.find_element_by_css_selector('div.office-info__hours').get_attribute('textContent')

            # Latitude
            lat = re.search('(\-?\d+(\.\d+)?),\s*(\-?\d+(\.\d+)?)', driver.find_element_by_css_selector('div.office-info__map').get_attribute('innerHTML').strip()).group().split(',')[0]

            # Longitude
            lon = re.search('(\-?\d+(\.\d+)?),\s*(\-?\d+(\.\d+)?)', driver.find_element_by_css_selector('div.office-info__map').get_attribute('innerHTML').strip()).group().split(',')[1]

            # Location type
            location_type = '<MISSING>'

            # Country
            country = 'US'

            locations_ids.append(location_id)
            locations_type.append(location_type)
            locations_titles.append(locations_title)
            street_addresses.append(street_address)
            cities.append(city)
            states.append(state)
            zip_codes.append(zip_code)
            phone_numbers.append(phone_number)
            hours.append(hour)
            countries.append(country)
            latitude_list.append(lat)
            longitude_list.append(lon)


        for (
                locations_title,
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
                location_type
        ) in zip(
            locations_titles,
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
            locations_type
        ):
            self.data.append(
                [
                    self.url,
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
