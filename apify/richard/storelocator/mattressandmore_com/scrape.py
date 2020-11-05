from Scraper import Scrape
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('mattressandmore_com')




URL = "https://mattressandmore.com/"


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

        location_url = 'https://ffohome.com/allshops'
        driver.get(location_url)
        stores = [info for info in driver.find_elements_by_css_selector('div.info-wrap')]

        for store in stores:
            # Store ID
            location_id = '<MISSING>'

            #Page Url
            page_url = store.find_element_by_css_selector('a.read-more').get_attribute('href')
            logger.info(page_url)
            # Type
            location_type = 'Mattress Retail'

            # Name
            location_title = store.find_element_by_css_selector('h2.shop-name > a').text

            # Street
            street_address = store.find_element_by_css_selector('div.ffo-store-loc > a > span:nth-of-type(1)').text

            # city
            city = store.find_element_by_css_selector('div.ffo-store-loc > a > span:nth-of-type(2)').text.split(',')[0]

            # zip
            zipcode = store.find_element_by_css_selector('div.ffo-store-loc > a > span:nth-of-type(2)').text.split(',')[1].strip()[-5:]

            # State
            state = store.find_element_by_css_selector('div.ffo-store-loc > a > span:nth-of-type(2)').text.split(',')[1].strip()[:-5]

            # Phone
            phone = store.find_element_by_css_selector('p.phone-number > a').text

            # Lat
            lat = store.find_element_by_css_selector('div.ffo-store-loc > a').get_attribute('href').split('/')[-1].split(',+')[0]

            # Long
            lon = store.find_element_by_css_selector('div.ffo-store-loc > a').get_attribute('href').split('/')[-1].split(',+')[1]

            # Hour
            hour = ' '.join([hour.get_attribute('textContent') for hour in store.find_elements_by_css_selector('div.ffo-store-hours > p')])

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
            if country == "<MISSING>":
                pass
            else:
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
