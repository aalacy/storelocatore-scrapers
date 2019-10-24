import requests

from Scraper import Scrape


URL = "https://mysagedental.com/"


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

        headers = {
            'Sec-Fetch-Mode': 'cors',
            'Referer': 'https://mysagedental.com/find-locations/',
            'DNT': '1',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36',
        }

        stores = requests.get('https://mysagedental.com/wp-content/themes/sharkbite-child/assets/js/google-maps-json.php', headers=headers).json()['features']


        for store in stores:
            # Store ID
            location_id = '<MISSING>'

            # Type
            location_type = store['properties']['category']

            # Name
            location_title = store['properties']['name']

            # Street
            street_address = store['properties']['address1'] + store['properties']['address2']

            # city
            city = store['properties']['city']

            # zip
            zipcode = store['properties']['zip']

            # State
            state = store['properties']['state']

            # Phone
            phone = store['properties']['phone']

            # Lat
            lat = store['geometry']['coordinates'][1]

            # Long
            lon = store['geometry']['coordinates'][0]

            # Hour
            hour = 'By appointment'

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