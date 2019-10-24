from Scraper import Scrape
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


URL = "https://www.muvfitness.com"


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

        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(self.CHROME_DRIVER_PATH, options=options)

        location_url = 'https://www.muvfitness.com/locations/'
        driver.get(location_url)
        stores = [info.get_attribute('href') for info in driver.find_elements_by_css_selector('li.location > div.bottom > div.buttons-wrap.flex > a:nth-of-type(2)')]

        for store in stores:
            driver.get(store)

            # Store ID
            location_id = '<MISSING>'

            # Type
            location_type = 'Gym'

            # Name
            location_title = driver.find_element_by_css_selector('header.h-spacer > strong').text

            # Street
            street_address = driver.find_element_by_css_selector('address > span:nth-of-type(1)').text

            # city
            city = driver.find_element_by_css_selector('address > span:nth-of-type(2)').text

            # zip
            zipcode = driver.find_element_by_css_selector('address > span:nth-of-type(4)').text

            # State
            state = driver.find_element_by_css_selector('address > span:nth-of-type(3)').text

            # Phone
            phone = driver.find_element_by_css_selector('a.phone-link').get_attribute('href').replace('tel:', '')

            # Lat
            lat = driver.find_element_by_css_selector('div.imap').get_attribute('data-latitude')

            # Long
            lon = driver.find_element_by_css_selector('div.imap').get_attribute('data-longitude')

            # Hour
            hour = driver.find_element_by_css_selector('div.gym-hours').get_attribute('textContent')

            # Country
            country = 'USA'

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
                location_type,
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
            location_types,
        ):
            if country == "<MISSING>":
                pass
            else:
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