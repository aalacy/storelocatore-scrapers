import requests

from Scraper import Scrape
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

URL = "https://parkerskitchen.com/"


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
        page_urls = []

        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(self.CHROME_DRIVER_PATH, options=options)

        headers = {
            'authority': 'parkerskitchen.com',
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'dnt': '1',
            'x-requested-with': 'XMLHttpRequest',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'referer': 'https://parkerskitchen.com/locations/',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-US,en;q=0.9,zh-TW;q=0.8,zh;q=0.7',
            'cookie': '_ga=GA1.2.139500414.1572317794; _gid=GA1.2.1376503009.1572317794; _gat=1',
        }

        params = (
            ('origAddress', '8120 US-280, Ellabell, GA 31308, USA'),
        )

        stores = requests.get('https://parkerskitchen.com/wp-content/themes/parkers/get-locations.php', headers=headers, params=params).json()

        for store in stores:
            # Store ID
            location_id = store['id']

            # Page website
            page_url = store['web']

            # Type
            location_type = 'Gas Station'

            # Name
            location_title = store['name']

            # Street
            street_address = store['address'] + ' ' + store['address2']

            # city
            city = store['city']

            # zip
            zipcode = store['postal']

            # State
            state = store['state']

            # Phone
            print(f"Currently scraping: {page_url}")
            driver.get(page_url)
            phone = driver.find_element_by_id('locations-text').find_element_by_css_selector('p').get_attribute('textContent').split('\n')[-1].strip()

            # Lat
            lat = store['lat']

            # Long
            lon = store['lng']

            # Hour
            hour = 'Open all day'

            # Country
            country = 'US'

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
                page_url
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
            page_urls
        ):
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
