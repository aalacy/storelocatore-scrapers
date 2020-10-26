import requests

from geopy.geocoders import Nominatim
from Scraper import Scrape

geolocator = Nominatim(user_agent="justsalad_com_scraper")
URL = "https://justsalad.com"


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
        stores = []

        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Referer': 'https://justsalad.com/locations',
            'DNT': '1',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
            'Sec-Fetch-Mode': 'cors',
        }

        params = (
            ('v', '1558558583021'),
        )

        stores = requests.get('https://justsalad.com/assets/geo/js.geojson', headers=headers, params=params).json()['features']

        for store in stores:
            latlon = store['geometry']

            # Lat
            lat = latlon['coordinates'][1]

            # Long
            lon = latlon['coordinates'][0]

            # Get loc info
            location = geolocator.reverse(f"{lat}, {lon}").raw

            # Country
            country = location['address']['country']

            if not store['properties']['locationID'][0].isalpha():
                store = store['properties']
                print(f"Now scraping {store['locationName']}")

                # Name
                location_title = store['locationName']

                # Store ID
                location_id = store['locationID']

                # Type
                location_type = 'Restaurant'

                # Street
                street_address = store['locationAddress']

                # Phone
                phone = store['locationPhone']

                # city
                city = location['address']['city'] if 'city' in location['address'].keys() else location['address']['county']

                # zip
                zipcode = location['address']['postcode']

                # State
                state = location['address']['state']

                # Hour
                hour = ' '.join([store['hours1'], store['hours2'], store['hours3']])

                if hour.strip() == '':
                    hour = '<MISSING>'

                # Country
                country = location['address']['country']

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