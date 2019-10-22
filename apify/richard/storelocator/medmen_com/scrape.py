import requests

from Scraper import Scrape


URL = "https://www.medmen.com/"


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
            'Sec-Fetch-Mode': 'cors',
            'Origin': 'https://www.medmen.com',
            'X-Contentful-User-Agent': 'sdk contentful.js/0.0.0-determined-by-semantic-release; platform browser; os macOS;',
            'Authorization': 'Bearer 3a1fbd8bd8285a5ebe9010b17959d62fed27abc42059373f3789023bb7863a06',
            'Accept': 'application/json, text/plain, */*',
            'Referer': 'https://www.medmen.com/stores',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36',
            'DNT': '1',
        }

        params = (
            ('content_type', 'store'),
        )

        stores = requests.get('https://cdn.contentful.com/spaces/1ehd3ycc3wzr/environments/master/entries', headers=headers, params=params).json()['items']

        print(f"{len(stores)} locations scraped.")


        for store in stores:
            store = store['fields']

            if 'comingSoon' not in store.keys() or not store['comingSoon']:

                # Store ID
                location_id = store['placeId']

                # Type
                location_type = 'Store'

                # Name
                location_title = store['title']

                # Street
                street_address = store['address']

                # city
                city = store['address2'].split(',')[0]

                # zip
                zipcode = store['address2'].split(',')[-1][-5:]

                # State
                state = store['state']

                # Phone
                phone = store['phoneNumber']

                # Lat
                lat = store['location']['lat']

                # Long
                lon = store['location']['lon']

                # Hour
                hour = store['storeHours']

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
