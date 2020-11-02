import requests

from Scraper import Scrape

URL = "https://www.redlobster.com/"


class Scraper(Scrape):
    def __init__(self, url):
        Scrape.__init__(self, url)
        self.data = []
        self.day_of_week = {
            '0': 'Sunday',
            '1': 'Monday',
            '2': 'Tuesday',
            '3': 'Wednesday',
            '4': 'Thursday',
            '5': 'Friday',
            '6': 'Saturday',
        }

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
            'authority': 'www.redlobster.com',
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'dnt': '1',
            'x-requested-with': 'XMLHttpRequest',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
            'content-type': 'application/json',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'referer': 'https://www.redlobster.com/locations/list',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-US,en;q=0.9,zh-TW;q=0.8,zh;q=0.7',
            'cookie': '__uzma=dccfb994-0683-47ca-bae6-07bd859f3672; __uzmb=1575948889; ASP.NET_SessionId=cl4nk1e23komfuip1ddn0eh0; rlClientType=0; __ssds=2; _gcl_au=1.1.574522558.1575948891; _ga=GA1.2.1753849678.1575948891; _gid=GA1.2.439459891.1575948891; _gat_UA-51406106-1=1; __ssuzjsr2=a9be0cd8e; __uzmaj2=14d4ab98-3b7a-421e-bc0e-4d4bf5e71839; __uzmbj2=1575948890; __uzmcj2=970361056753; __uzmdj2=1575948890; _fbp=fb.1.1575948890735.1677962216; _derived_epik=dj0yJnU9MzZRUVQxZ3kyUUVmeE1sdnUyOTZ4MklKaGpsYkNfSjUmbj1iMUR1cDR0T3dQY2t1VnBReXlVRUNRJm09NyZ0PUFBQUFBRjN2RWxv; __uzmc=655741659984; __uzmd=1575948903',
        }

        params = (
            ('latitude', '37.5952304'),
            ('longitude', '-122.043969'),
            ('radius', '200000'),
            ('limit', '99999999999'),
        )

        stores = requests.get('https://www.redlobster.com/api/location/GetLocations', headers=headers, params=params).json()['locations']

        for store in stores:
            store = store['location']

            # Store ID
            location_id = store['rlid']

            # Name
            location_title = f"Red Lobster -  {store['city']}"

            # Page url
            page_url = store['localPageURL']

            # Type
            location_type = 'Restaurant'

            # Street
            street_address = store['address1']

            # city
            city = store['city']

            # zip
            zipcode = store['zip']

            # State
            state = store['state']

            # Phone
            phone = store['phone']

            # Lat
            lat = store['latitude']

            # Long
            lon = store['longitude']

            # Hour
            hour = ' '.join([
                f"{self.day_of_week[str(hour['dayOfWeek'])]}: {hour['open']} to {hour['close']}" for hour in store['hours']
            ])

            # Country
            country = 'US'

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
