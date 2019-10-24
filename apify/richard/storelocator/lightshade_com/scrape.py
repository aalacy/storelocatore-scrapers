import requests

from Scraper import Scrape


URL = "https://lightshade.com/"


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
            'cookie': '_ga=GA1.2.698476805.1570930725; _gid=GA1.2.929549293.1570930725; _gat_UA-54747737-1=1; age_gate=21',
            'dnt': '1',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-US,en;q=0.9,zh-TW;q=0.8,zh;q=0.7',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'referer': 'https://lightshade.com/locations/',
            'authority': 'lightshade.com',
            'x-requested-with': 'XMLHttpRequest',
            'sec-fetch-site': 'same-origin',
        }

        params = (
            ('action', 'asl_load_stores'),
            ('nonce', '97453abb26'),
            ('load_all', '1'),
            ('layout', '1'),
        )

        stores = requests.get('https://lightshade.com/wp-admin/admin-ajax.php', headers=headers, params=params).json()


        for store in stores:
            # Store ID
            location_id = store['id']

            # Type
            location_type = 'Store'

            # Name
            location_title = store['title']

            # Street
            street_address = store['street']

            # city
            city = store['city']

            # zip
            zipcode = store['postal_code']

            # State
            state = store['state']

            # Phone
            phone = store['phone']

            # Lat
            lat = store['lat']

            # Long
            lon = store['lng']

            # Hour
            hour = f"Daily Start time:{store['start_time_0']} Daily End time: {store['end_time_0']}"

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
            if country == "<MISSING>":
                pass
            else:
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