import requests
import json

from Scraper import Scrape
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('acehotel_com')



URL = "https://www.acehotel.com"


class Scraper(Scrape):
    def __init__(self, url):
        Scrape.__init__(self, url)
        self.data = []
        self.block = ['Ace Hotel Kyoto | Ace Hotel Kyoto', 'Ace Hotel London | Ace Hotel London']

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
            'x-newrelic-id': 'VQAHWVFSGwEAVVVQAAEFXg==',
            'dnt': '1',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-US,en;q=0.9,zh-TW;q=0.8,zh;q=0.7',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
            'accept': 'application/json, text/plain, */*',
            'referer': 'https://www.acehotel.com/locations/',
            'authority': 'www.acehotel.com',
            'cookie': 'csrftoken=jXyb38XIf4Hd3nLkCObyUsUUb91X8KV5s1E1jk4UCgRI5UeXcjXplC8zgdvev1ph; _gcl_au=1.1.553951305.1568512822; _fbp=fb.1.1568512822621.199288418; _ga=GA1.2.978627245.1568512849; gwcc=%7B%22fallback%22%3A%223125481177%22%2C%22clabel%22%3A%22cuVoCOzEu3EQ9ZuulgM%22%2C%22backoff%22%3A86400%2C%22backoff_expires%22%3A1569298706%7D; _gid=GA1.2.526416788.1570423537; _gat_UA-4157266-1=1',
            'sec-fetch-site': 'same-origin',
        }

        params = (
            ('type', 'tupac.Hotel'),
        )

        response = requests.get('https://www.acehotel.com/api/v2/pages/', headers=headers, params=params)

        stores = [item['meta']['detail_url'] for item in json.loads(response.content)['items']]

        for store in stores:
            logger.info(store)
            r = json.loads((requests.get(store)).content)
            if r['construct_title'] not in self.block:
                # Store ID
                location_id = r['id']

                # Name
                location_title = r['hotel_data']['title']

                # Type
                location_type = 'Hotel'

                # Country
                country = "US"

                # State
                state = r['address'].split(',')[-1].strip()[:2]

                # city
                city = r['address'].split(',')[1] if len(r['address'].split(',')) == 3 else r['construct_title'].split('|')[0].strip().replace('Ace Hotel', '').strip()

                # zip
                zipcode = r['address'].split(',')[-1].strip()[2:].strip()

                # Street
                street_address = r['address'].split(',')[0].strip().replace(city, '')

                # Lat
                lat = r['latitude']

                # Long
                lon = r['longitude']

                # Phone
                phone = r['telephone']

                # hour
                hour = "Always Open"

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
