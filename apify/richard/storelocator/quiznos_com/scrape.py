import requests
import json

from Scraper import Scrape


URL = "https://quiznos.com"


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

        headers = {
            'sec-fetch-mode': 'cors',
            'dnt': '1',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-US,en;q=0.9,zh-TW;q=0.8,zh;q=0.7',
            'x-requested-with': 'XMLHttpRequest',
            'cookie': '_ga=GA1.2.1618618586.1571897170; _gid=GA1.2.709127164.1571897170; _gat_gtag_UA_5401627_1=1; _gat=1; __cfduid=db0907bce0aee4287969d559dbcbe0c951571897173',
            'if-modified-since': 'Thu, 24 Oct 2019 06:00:02 GMT',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36',
            'accept': 'text/javascript, application/javascript, application/ecmascript, application/x-ecmascript, */*; q=0.01',
            'referer': 'https://restaurants.quiznos.com/',
            'authority': 'restaurants.quiznos.com',
            'if-none-match': 'W/"262d9-16dfc59bad0"',
            'sec-fetch-site': 'same-origin',
        }

        params = (
            ('callback', 'storeList'),
        )

        stores = requests.get("https://restaurants.quiznos.com/data/stores.json?callback=storeList").content
        stores = json.loads(stores.decode().replace('storeList(', '')[:-1])

        for store in stores:
            # Store ID
            location_id = store['storeid']

            # Type
            location_type = 'Restaurant'

            # Name
            location_title = store['restaurantname']

            # Street
            street_address = store['address1'] + store['address2']

            # city
            city = store['city']

            # zip
            zipcode = store['zipcode']

            # State
            state = store['statecode']

            # Lat
            lat = store['latitude']

            # Long
            lon = store['longitude']

            # Phone
            phone = store['phone']

            # Hour
            hour = 'Everyday: ' + store['businesshours']

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


scrape = Scraper(URL)
scrape.scrape()