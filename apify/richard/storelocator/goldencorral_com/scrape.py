import requests

from Scraper import Scrape
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

URL = "https://www.goldencorral.com/"


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
        stores = []
        page_urls = []
        store_hours = {}

        headers = {
            'authority': 'www.goldencorral.com',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36',
            'dnt': '1',
            'accept': '*/*',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'referer': 'https://www.goldencorral.com/locations/',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-US,en;q=0.9,zh-TW;q=0.8,zh;q=0.7',
            'cookie': '_ga=GA1.2.8386502.1571548028; _gcl_au=1.1.1596113616.1571548029; _fbp=fb.1.1571548029699.1130326595; _gid=GA1.2.729568158.1572068476; _gat=1',
        }
        stores.extend(requests.get('https://www.goldencorral.com/wp-json/locator/v1/search/46.06/-109.14/42.61/-125.12/49.32/-93.17/', headers=headers).json())
        stores.extend(requests.get('https://www.goldencorral.com/wp-json/locator/v1/search/38.85/-107.91/34.99/-123.89/42.51/-91.94/', headers=headers).json())
        stores.extend(requests.get('https://www.goldencorral.com/wp-json/locator/v1/search/33.3/-105.31/29.17/-121.29/37.24/-89.34/', headers=headers).json())
        stores.extend(requests.get('https://www.goldencorral.com/wp-json/locator/v1/search/31.22/-84.22/27/-100.19/35.26/-68.24/', headers=headers).json())
        stores.extend(requests.get('https://www.goldencorral.com/wp-json/locator/v1/search/38.76/-83.78/34.89/-99.75/42.43/-67.81/', headers=headers).json())
        stores.extend(requests.get('https://www.goldencorral.com/wp-json/locator/v1/search/43.93/-82.09/40.35/-98.07/47.31/-66.12/', headers=headers).json())

        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(self.CHROME_DRIVER_PATH, options=options)
        driver.get("https://www.goldencorral.com/all-locations/")
        store_links = [link.get_attribute('href') for link in driver.find_elements_by_css_selector('div.all-locations-item > a.primary-link')]

        for store_link in store_links:
            print(f'Getting info for store {store_link}')
            driver.get(store_link)
            link = store_link.replace('https://', '').strip('/').split('/')[2]
            try:
                hour = driver.find_element_by_css_selector('ul.location-detail-hours').get_attribute('textContent')
            except:
                hour = '<MISSING>'
            store_hours[link] = {
                'hour': hour,
                'store_link': store_link
            }


        for store in stores:
            if store['opening_soon'] != "1" and store['customer'] not in self.seen:
                # Store ID
                location_id = store['customer']

                # Page url
                page_url = store_hours[location_id]['store_link']

                # Type
                location_type = 'Restaurant'

                # Name
                location_title = store['company']

                # Street
                street_address = store['address']

                # city
                city = store['city']

                # zip
                zipcode = store['zip']

                # State
                state = store['state']

                # Phone
                phone = store['phone']

                # Lat
                lat = store['lat']

                # Long
                lon = store['lng']

                # Hour
                hour = store_hours[location_id]['hour']

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
                self.seen.append(store['customer'])

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
