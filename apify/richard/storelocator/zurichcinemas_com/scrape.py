from Scraper import Scrape
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


URL = "http://www.zurichcinemas.com"


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

        location_url = 'http://www.zurichcinemas.com/'
        driver.get(location_url)
        stores = [content.get_attribute('onclick')[22:-1] for content in driver.find_elements_by_css_selector('ul.zul > li')]

        for store in stores:
            driver.get(store)

            locations_ids.append('<MISSING>')

            locations_titles.append(driver.find_element_by_id('leftcinemaname').find_element_by_css_selector('b').text)

            location_info = driver.find_element_by_id('leftcinemaname').get_attribute('innerHTML').split('<br>')[1:-1]
            length = len(location_info)
            city_state = location_info[2].strip() if length == 5 else location_info[1].strip()

            # Street address
            street_addresses.append(location_info[1].strip() if length == 5 else location_info[0].strip())

            # City
            cities.append(city_state.split(',')[0].strip())

            # State
            states.append(city_state.split(',')[1].strip()[:-5].strip())

            # zipcode
            zip_codes.append(city_state.split(',')[1].strip()[-5:])

            # Country
            countries.append('US')

            # Hours
            hours.append('<MISSING>')

            # Latitude
            latitude_list.append('<MISSING>')

            # Long
            longitude_list.append('<MISSING>')

            # Phone
            phone_numbers.append(location_info[-2].strip())

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
