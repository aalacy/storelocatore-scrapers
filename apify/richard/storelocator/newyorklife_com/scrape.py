import sgzip

from Scraper import Scrape
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


URL = "https://www.newyorklife.com"


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

        for zipcode_search in sgzip.for_radius(100):
            location_url = f'https://www.newyorklife.com/nylife/dispatcher/searchAgentsBySingleLineAddress?singleLineAddress={zipcode_search}&distance=100'
            driver.get(location_url)

            length = len([content.get_attribute('id') for content in driver.find_elements_by_css_selector('div.contact-agent')])

            locations_ids.extend([content.get_attribute('id') for content in driver.find_elements_by_css_selector('div.contact-agent')])
            locations_titles.extend([content.get_attribute('textContent') for content in driver.find_elements_by_css_selector('div.name > a')])
            street_addresses.extend([content.get_attribute('textContent') for content in driver.find_elements_by_css_selector('div.address.one')])
            cities.extend([content.get_attribute('textContent').split(',')[0] for content in driver.find_elements_by_css_selector('div.city-state-zip')])
            states.extend([content.get_attribute('textContent').split(',')[1].strip()[:2] for content in driver.find_elements_by_css_selector('div.city-state-zip')])
            zip_codes.extend([content.get_attribute('textContent').split(',')[1].strip()[2:] for content in driver.find_elements_by_css_selector('div.city-state-zip')])
            phone_numbers.extend([content.get_attribute('textContent') for content in driver.find_elements_by_css_selector('div.phone > a')])

            latitude_list.extend(['<MISSING>'] * length)
            longitude_list.extend(['<MISSING>'] * length)
            hours.extend(['<MISSING>'] * length)
            countries.extend(['US'] * length)

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
