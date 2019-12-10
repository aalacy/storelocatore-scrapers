import requests
import json
import sgzip

from Scraper import Scrape

URL = "https://www.foodlion.com/"


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
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Referer': 'https://www.foodlion.com//stores/',
            'DNT': '1',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.87 Safari/537.36',
        }

        for coord_search in sgzip.coords_for_radius(50):
            params = (
                ('zip', 'Salisbury, North Carolina'),
                ('lat', coord_search[0]),
                ('lng', coord_search[1]),
                ('distance', '50'),
                ('onlyPharmacyEnabledStores', 'false'),
            )
            data = json.loads(requests.get('https://www.foodlion.com/bin/foodlion/search/storelocator.json', headers=headers, params=params).json()['result'])
            stores.extend(data)
            print(f"{len(data)} locations scraped for {coord_search[0]}, {coord_search[1]}")

        for store in stores:
            if store['id'] not in self.seen:
                # Store ID
                location_id = store['id']

                # Name
                location_title = store['title']

                # Page url
                page_url = store['href']

                # Type
                location_type = 'Grocery Store'

                # Street
                street_address = store['address']

                # city
                city = store['city']

                # zip
                zipcode = store['zip']

                # State
                state = store['state']

                # Phone
                phone = store['phoneNumber']

                # Lat
                lat = store['lat']

                # Long
                lon = store['lon']

                # Hour
                hour = ' '.join(store['hours'])

                # Country
                country = 'USA'

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
                self.seen.append(location_id)

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
