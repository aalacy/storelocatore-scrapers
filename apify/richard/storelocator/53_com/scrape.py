import sgzip
import requests

from Scraper import Scrape


URL = "https://www.53.com/"


class Scraper(Scrape):
    def __init__(self, url):
        Scrape.__init__(self, url)
        self.data = []
        self.block = ['https://www.miravalspamonarchbeach.com/', 'https://www.miravalstkitts.com/']
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
        stores = []

        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Referer': 'https://locations.53.com/search.html',
            'Origin': 'https://locations.53.com',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
            'DNT': '1',
            'Sec-Fetch-Mode': 'cors',
        }

        for zipcode_search in sgzip.for_radius(50):
            params = (
                ('q', zipcode_search),
                ('types', '3233|3234|3235'),
            )

            data = requests.get('https://tcjl25l2al.execute-api.us-east-1.amazonaws.com/prod', headers=headers, params=params).json()['locations']
            stores.extend(data)
            print(f"{len(data)} locations scraped for {zipcode_search}")

        for store in stores:
            store = store['loc']

            if store['id'] not in self.seen:
                # Store ID
                location_id = store['id']

                # Type
                location_type = 'ATM' if len(store['hours']['days']) == 0 else 'Branch'

                # Name
                location_title = f"Fifth Third Bank - {store['city']}"

                # Street
                street_address = store['address1'] + store['address2']

                # city
                city = store['city']

                # zip
                zipcode = store['postalCode']

                # State
                state = store['state']

                # Phone
                phone = store['phone']

                # Lat
                lat = store['latitude']

                # Long
                lon = store['longitude']

                # Hour
                hour = store['hours']['days'] if len(store['hours']['days']) != 0 else 'Always Open'

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
                self.seen.append(store['id'])

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