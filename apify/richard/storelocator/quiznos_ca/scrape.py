import requests
import json

from Scraper import Scrape
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options

URL = "http://www.quiznos.ca/"


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
        # options = Options()
        # options.add_argument("--headless")
        # options.add_argument("--no-sandbox")
        # options.add_argument("--disable-dev-shm-usage")
        # driver = webdriver.Chrome(self.CHROME_DRIVER_PATH, options=options)
        # driver.get("http://www.unitedoilco.com/locations?brand=foodmart")
        # stores = [url.get_attribute('href') for url in driver.find_element_by_css_selector('table.list-of-station > tbody').find_elements_by_css_selector('a')]
        cookies = {
            '__cfduid': 'd82dfb12617981c4e27a6fc54ee62636e1575263726',
            '_ga': 'GA1.2.417765513.1575263727',
            '_gid': 'GA1.2.1371239866.1575263727',
            '_gat': '1',
            '_fbp': 'fb.1.1575263727676.889926137',
            'lang': 'en',
            'QSI_HistorySession': 'http%3A%2F%2Frestaurants.quiznos.ca%2F~1575263732502',
        }

        headers = {
            'Connection': 'keep-alive',
            'Accept': 'text/javascript, application/javascript, application/ecmascript, application/x-ecmascript, */*; q=0.01',
            'DNT': '1',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.87 Safari/537.36',
            'Referer': 'http://restaurants.quiznos.ca/',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US,en;q=0.9,zh-TW;q=0.8,zh;q=0.7',
            'If-None-Match': 'W/"1370f-16ec503f428"',
            'If-Modified-Since': 'Mon, 02 Dec 2019 05:10:01 GMT',
        }

        params = (
            ('callback', 'storeList'),
        )

        stores = json.loads(requests.get('http://restaurants.quiznos.ca/data/stores.json?callback=storeList').content.decode("utf-8").replace('storeList(', '')[:-1])

        for store in stores:
            # Store ID
            location_id = store['storeid']

            # Name
            location_title = store['restaurantname']

            # Page url
            page_url = URL + store['url']

            # Type
            location_type = 'Restaurant'

            # Street
            street_address = store['address1'] + ' ' + store['address2']

            # city
            city = store['city']

            # zip
            zipcode = store['zipcode']

            # State
            state = store['statecode']

            # Phone
            phone = store['phone']

            # Lat
            lat = store['latitude']

            # Long
            lon = store['longitude']

            # Hour
            hour = 'Everyday - ' + store['businesshours'] if store['businesshours'].strip() != '' else '<MISSING>'

            # Country
            country = 'Canada'

            # Store data
            locations_ids.append(location_id)
            page_urls.append(page_url)
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
        # driver.quit()


scrape = Scraper(URL)
scrape.scrape()
