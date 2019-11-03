import requests

from Scraper import Scrape

URL = "https://scooterscoffee.com/"


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
        stores = []

        headers = {
            'authority': 'scooterscoffee.com',
            'accept': '*/*',
            'dnt': '1',
            'x-requested-with': 'XMLHttpRequest',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'referer': 'https://scooterscoffee.com/locations/',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-US,en;q=0.9,zh-TW;q=0.8,zh;q=0.7',
            'cookie': '_ga=GA1.2.81002375.1572410384; _gid=GA1.2.1940358607.1572410384; _gat_gtag_UA_115776230_1=1; _fbp=fb.1.1572410384576.441128402',
        }

        params = (
            ('action', 'store_search'),
            ('lat', '41.252363'),
            ('lng', '-95.99798800000002'),
            ('max_results', '10'),
            ('search_radius', '10'),
        )

        stores = requests.get('https://scooterscoffee.com/wp-admin/admin-ajax.php', headers=headers, params=params).json()

        for store in stores:
            if store['id'] not in self.seen:
                # Store ID
                location_id = store['id']

                # Page website
                page_url = store['url'] if len(store['url']) > 0 else '<MISSING>'

                # Type
                location_type = 'Convenience Store'

                # Name
                location_title = store['store']

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
                hour = store['hours'] if len(store['hours']) > 0 else '<MISSING>'

                # Country
                country = store['country']

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
                self.seen.append(location_id)

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


scrape = Scraper(URL)
scrape.scrape()
