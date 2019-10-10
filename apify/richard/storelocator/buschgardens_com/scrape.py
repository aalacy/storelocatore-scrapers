from Scraper import Scrape
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait


URL = "https://buschgardens.com/"


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
        stores = []

        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(self.CHROME_DRIVER_PATH, options=options)

        location_url = 'https://buschgardens.com/'
        driver.get(location_url)

        stores.extend(driver.find_elements_by_css_selector('li.two-col-content__item > a'))
        stores = [store.get_attribute('href') for store in stores]


        for store in stores:
            driver.get(store)

            wait = WebDriverWait(driver, 10)
            wait.until(ec.visibility_of_element_located((By.CSS_SELECTOR, "div.footer")))

            location_info = driver.find_element_by_css_selector('div.footer-contentinfo__wrapper.container > p').get_attribute('innerHTML').replace('© 2019 SeaWorld Parks &amp; Entertainment, Inc. All Rights Reserved.', '').strip()

            # Store ID
            location_id = '<MISSING>'

            # City
            city = location_info.split(',')[1].strip()

            # Name
            location_title = city

            # Street Address
            street_address = location_info.split(',')[0]

            # State
            state = location_info.split(',')[2][:-5]

            # Zip
            zip_code = location_info.split(',')[2][-5:]

            # Hours
            hour = '<MISSING>'

            # Lat
            lat = '<MISSING>'

            # Lon
            lon = '<MISSING>'

            # Phone
            phone = phone = [info.get_attribute('innerHTML') for info in driver.find_elements_by_css_selector('span.contact-links-listing__link-text') if info.get_attribute('innerHTML') != 'Email Us'][0]

            # Country
            country = "US"

            # Store data
            locations_ids.append(location_id)
            locations_titles.append(location_title)
            street_addresses.append(street_address)
            states.append(state)
            zip_codes.append(zip_code)
            hours.append(hour)
            latitude_list.append(lat)
            longitude_list.append(lon)
            phone_numbers.append(phone)
            cities.append(city)
            countries.append(country)

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
