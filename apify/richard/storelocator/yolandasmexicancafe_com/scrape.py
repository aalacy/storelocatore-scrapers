from Scraper import Scrape
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


URL = "http://yolandasmexicancafe.com/"


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

        location_url = 'http://yolandasmexicancafe.com/'
        driver.get(location_url)
        stores = list(set([content.get_attribute('href') for content in driver.find_elements_by_css_selector('ul.sf-menu.pm-nav.sf-js-enabled > li:nth-of-type(3) > ul > li > a')]))

        for store in stores:
            driver.get(store)

            location_id = '<MISSING>'

            locations_title = driver.find_element_by_css_selector('p.pm-sub-header-title > span').text

            location_info = driver.find_element_by_css_selector('div.col-lg-4.col-md-4.col-sm-4.pm-column-spacing > p:nth-of-type(1)').text.split('\n')

            street_address = location_info[0]

            city = location_info[1].split(',')[0]

            state = location_info[1].split(',')[1].strip()[:-5]

            country = 'US'

            zip_code = location_info[1].split(',')[1].strip()[-5:]

            phone_number = driver.find_element_by_css_selector('div.col-lg-4.col-md-4.col-sm-4.pm-column-spacing > p:nth-of-type(2)').get_attribute('textContent')

            hour = driver.find_element_by_css_selector('div.col-lg-4.col-md-4.col-sm-4.pm-column-spacing > p:nth-of-type(4)').get_attribute('textContent')

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
