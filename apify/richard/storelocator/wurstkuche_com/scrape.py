import re

from Scraper import Scrape
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


URL = "https://www.wurstkuche.com"


class Scraper(Scrape):
    def __init__(self, url):
        Scrape.__init__(self, url)
        self.data = []
        self.seen = []
        self.postal_codes = []

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

        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(self.CHROME_DRIVER_PATH, options=options)

        location_url = 'https://www.wurstkuche.com'
        driver.get(location_url)
        stores = driver.find_element_by_id('page-56538a4ee4b0e74bc86c4cc4').find_elements_by_css_selector('div.row.sqs-row')

        for store in stores:
            if store.get_attribute('id') != '':
                locations_title = store.find_element_by_css_selector('div.sqs-block-content > h1').text

                location_info = store.find_element_by_css_selector('div.sqs-block-content > p:nth-of-type(2) > a').text
                city_state = re.search('(\w+\s?\w+,\s\w{2}\s\d{5}$)', location_info).group()

                street_address = location_info.replace(city_state, '').strip()

                city = city_state.split(',')[0]

                state = city_state.split(',')[1].strip()[:-5]

                country = 'US'

                zip_code = city_state.split(',')[1].strip()[-5:]

                hour = store.find_element_by_css_selector('div.sqs-block-content > p:nth-of-type(3)').get_attribute('textContent')

                phone_number = re.search('\d+.\d+.\d+\sext\s\d', store.find_element_by_css_selector('div.sqs-block-content > p:nth-of-type(4)').get_attribute('textContent')).group()

                location_id = '<MISSING>'

                lat = '<MISSING>'

                lon = '<MISSING>'

                locations_ids.append(location_id)
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
                    "<MISSING>",
                    latitude,
                    longitude,
                    hour,
                ]
            )

        driver.quit()


scrape = Scraper(URL)
scrape.scrape()
