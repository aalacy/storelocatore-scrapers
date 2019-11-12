import requests
import re

from Scraper import Scrape

URL = "https://truenorthstores.com/"


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

        headers = {
            'authority': 'truenorthstores.com',
            'accept': '*/*',
            'origin': 'https://truenorthstores.com',
            'x-requested-with': 'XMLHttpRequest',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.87 Safari/537.36',
            'dnt': '1',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'referer': 'https://truenorthstores.com/stores/',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-US,en;q=0.9,zh-TW;q=0.8,zh;q=0.7',
            'cookie': '_ga=GA1.2.464637378.1572821645; _fbp=fb.1.1572821645634.631702491; tk_ai=woo%3AIBfz6ik4dbyIURiyR96AR3%2FJ; _gid=GA1.2.494985078.1573077411; _gat=1; _gat_All-Starhttps%3A%2F%2Ftruenorthstores.com%2F=1; _gat_All-Starhttps%3A%2F%2Ftruenorthstores.com%2Fstores%2F=1',
        }

        data = {
            'action': 'locate',
            'address': '44141',
            'formatted_address': 'Brecksville, OH 44141, USA',
            'locatorNonce': 'fd493dfdf5',
            'distance': '100',
            'latitude': '41.3055951',
            'longitude': '-81.61446799999999',
            'unit': 'miles',
            'geolocation': 'false',
            'allow_empty_address': 'false'
        }

        response = requests.post('https://truenorthstores.com/wp-admin/admin-ajax.php', headers=headers, data=data)
        stores = response.json()['results']

        for store in stores:
            # Store ID
            location_id = store['id']

            # Type
            location_type = 'Coffee'

            # Page url
            page_url = store['permalink']

            # Name
            location_title = store['title']

            # Street
            street_address = re.sub('<[^>]*>', '', store['output']).split('\n')[2]

            # city
            city = re.sub('<[^>]*>', '', store['output']).split('\n')[3].split(',')[0]

            # zip
            zipcode = re.sub('<[^>]*>', '', store['output']).split('\n')[3].split(',')[1].strip()[2:]

            # State
            state = re.sub('<[^>]*>', '', store['output']).split('\n')[3].split(',')[1].strip()[:2]

            # Phone
            phone = re.sub('<[^>]*>', '', store['output']).split('\n')[4]

            # Lat
            lat = store['latitude']

            # Long
            lon = store['longitude']

            # Hour
            hour = re.sub('<[^>]*>', '', store['output']).split('\n')[5]

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
