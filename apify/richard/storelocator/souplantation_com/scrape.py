import re
import requests
from Scraper import Scrape

URL = "https://souplantation.com/"


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

        headers = {
            'authority': 'souplantation.com',
            'accept': '*/*',
            'dnt': '1',
            'x-requested-with': 'XMLHttpRequest',
            'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Mobile Safari/537.36',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'referer': 'https://souplantation.com/find-us/',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-US,en;q=0.9,zh-TW;q=0.8,zh;q=0.7',
            'cookie': '_ga=GA1.2.1468159589.1572926492; _gid=GA1.2.288343659.1572926492; _gat=1; _gcl_au=1.1.915883074.1572926492; _fbp=fb.1.1572926491923.99321884; PHPSESSID=15ci7gddictrm6mkesjts1ktv8; __atuvc=3%7C45; __atuvs=5dc0f41b7bb9ec7c002',
        }

        params = (
            ('action', 'store_search'),
            ('lat', '37.5952304'),
            ('lng', '-122.043969'),
            ('max_results', '999'),
            ('search_radius', '25'),
            ('autoload', '1'),
        )

        stores = requests.get('https://souplantation.com/wp-admin/admin-ajax.php', headers=headers, params=params).json()

        for store in stores:
            # Store ID
            location_id = store['store_number']

            # Page url
            page_url = store['permalink']

            # Type
            location_type = 'Restaurant'

            # Name
            location_title = store['store'] + '-' + store['city']

            # Street
            street_address = store['address'] + ' ' + store['address2']

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
            hour = re.sub('<.*?>', '', store['hours'])

            # Country
            country = store['country']

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


scrape = Scraper(URL)
scrape.scrape()
