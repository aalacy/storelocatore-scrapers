import requests

from pypostalcode import PostalCodeDatabase
from Scraper import Scrape
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('homesense_ca')




URL = "https://www.homesense.ca/"

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
        page_urls = []
        location_types = []
        stores = []
        pcdb = PostalCodeDatabase()
        pc = 'T3Z'
        radius = 3000
        results = pcdb.get_postalcodes_around_radius(pc, radius)
        coords = [(p.latitude, p.longitude) for p in results]
        headers = {
            'Connection': 'keep-alive',
            'Accept': 'application/json, text/plain, */*',
            'Origin': 'https://www.homesense.ca',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Mobile Safari/537.36',
            'DNT': '1',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Sec-Fetch-Site': 'cross-site',
            'Sec-Fetch-Mode': 'cors',
            'Referer': 'https://www.homesense.ca/en/storelocator',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9,zh-TW;q=0.8,zh;q=0.7',
        }

        for coord in coords[::10]:
            data = {
                'chain': '90,91,93',
                'geolat': str(coord[0]),
                'geolong': str(coord[1]),
                'lang': 'en',
                'maxstores': '100'
            }
            data = requests.post('https://mktsvc.tjx.com/storelocator/GetSearchResults', headers=headers, data=data).json()['Stores']
            stores.extend(data)
            logger.info(f"{len(data)} locations scraped for {coord[0]}, {coord[1]}")

        for store in stores:
            if ' '.join(store['Address'].split(' ')[:2]) not in self.seen:
                # Store ID
                location_id = store['StoreID']

                # Type
                location_type = '<MISSING>'

                # Page url
                page_url = '<MISSING>'

                # Name
                location_title = store['Name']

                # Street
                street_address = store['Address']

                # city
                city = store['City']

                # zip
                zipcode = store['Zip']

                # State
                state = store['State']

                # Lat
                lat = store['Latitude']

                # Long
                lon = store['Longitude']

                # Phone
                phone = store['Phone']

                # Hour
                hour = store['Hours']

                # Country
                country = store['Country']

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
                self.seen.append(' '.join(store['Address'].split(' ')[:2]))

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