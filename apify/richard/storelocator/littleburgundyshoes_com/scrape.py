from Scraper import Scrape
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


URL = "https://www.littleburgundyshoes.com"


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

        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(self.CHROME_DRIVER_PATH, options=options)

        location_url = 'https://www.littleburgundyshoes.com/stores'
        driver.get(location_url)
        stores = driver.find_elements_by_css_selector('div.store.panel-group')

        for store in stores:
            # Store ID
            location_id = '<MISSING>'

            # Type
            location_type = '<MISSING>'

            # Name
            location_title = store.find_element_by_css_selector('span.storeName').text

            # Street
            street_address = store.find_element_by_css_selector('div.panel-body > p > span:nth-of-type(1)').get_attribute('textContent').replace('\n', ' ')

            # city
            city = store.find_element_by_css_selector('div.panel-body > p > span:nth-of-type(2)').get_attribute('textContent')

            # zip
            zipcode = store.find_element_by_css_selector('div.panel-body > p > span:nth-of-type(5)').get_attribute('textContent')

            # State
            state = store.find_element_by_css_selector('div.panel-body > p > span:nth-of-type(3)').get_attribute('textContent')

            # Lat
            lat = '<MISSING>'

            # Long
            lon = '<MISSING>'

            # Phone
            phone = store.find_element_by_css_selector('div.phone > a > span').get_attribute('textContent')

            # Hour
            hour = store.find_element_by_css_selector('div.hours').get_attribute('textContent').replace('\n', ' ')

            # Country
            country = 'CA'

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
