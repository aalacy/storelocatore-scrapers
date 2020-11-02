import requests

from Scraper import Scrape


URL = "https://web.aw.ca/"


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
            'Referer': 'https://web.aw.ca/en/locations/',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36',
            'DNT': '1',
        }

        stores = requests.get('https://web.aw.ca/api/locations/', headers=headers).json()


        for store in stores:
            # Name
            location_title = store['restaurant_name']

            # Store ID
            location_id = store['restnum']

            # Page url
            page_url = '<MISSING>'

            # Type
            location_type = 'Fast Food'

            # Street
            street_address = store['address1'] + store['address2']

            # city
            city = store['city_name']

            # zip
            zipcode = store['postal_code']

            # State
            state = store['province_code']

            # Phone
            phone = store['phone_number']

            # Lat
            lat = store['latitude']

            # Lon
            lon = store['longitude']

            # Hour
            hour = ' '.join([
                'Sunday: ' + store['hours'][0],
                'Monday: ' + store['hours'][1],
                'Tuesday: ' + store['hours'][2],
                'Wednesday: ' + store['hours'][3],
                'Thursday: ' + store['hours'][4],
                'Friday: ' + store['hours'][5],
                'Saturday: ' + store['hours'][6],
                ])

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