import requests
import sgzip

from Scraper import Scrape


URL = "https://www.dickeys.com"


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
        stores = []

        cookies = {
            '_ga': 'GA1.2.11063676.1571548095',
            '_gid': 'GA1.2.442833860.1571548095',
            '_gat_gtag_UA_17819507_6': '1',
            '_fbp': 'fb.1.1571548095427.1223746656',
            'userWantsSubscribe': '0',
            '__adroll_fpc': 'a16578837e4b757f977f4efea0669515-s2-1571548105952',
            '__ar_v4': 'N6MRG2LYVFCW7HGWOA2BCR%3A20191019%3A2%7CAPUDEELEAFBZ7NZ6AXT7JS%3A20191019%3A2%7CTZDL75WXAVHA3JVBBNU7VP%3A20191019%3A2',
            'street_number': '',
            'route': '',
            'postal_code': '94587',
            'locality': 'Union City',
            'administrative_area_level_1': 'California',
            'lat': '37.5952304',
            'lng': '-122.043969',
            'addressInputString': '94587Union City, CA, USA',
        }

        headers = {
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Origin': 'https://www.dickeys.com',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9,zh-TW;q=0.8,zh;q=0.7',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Accept': '*/*',
            'Referer': 'https://www.dickeys.com/location',
            'X-Requested-With': 'XMLHttpRequest',
            'Connection': 'keep-alive',
            'DNT': '1',
        }

        for coords in sgzip.coords_for_radius(50):
            data = {
                'lat': f"{coords[0]}",
                'lng': f"{coords[1]}"
            }
            try:
                data = requests.post('https://www.dickeys.com/location/find-location-new', headers=headers, cookies=cookies, data=data).json()
                stores.extend(data)
                print(f"{len(data)} locations scraped for coordinates: {coords[0]} {coords[1]}")
            except:
                print(f"0 locations scraped for coordinates: {coords[0]} {coords[1]}")


        for store in stores:
            if store['body']['store_number'] not in self.seen and (store['body']['active'] if 'active' in store['body'].keys() else True):
                # hour
                hour = ' '.join(store['meta']['open_close_info'])

                store = store['body']

                # Store ID
                location_id = store['store_number']

                # Type
                location_type = 'Wellness and Resort'

                # Name
                location_title = f"Dickeys - {store['store_city']}"

                # Street
                street_address = store['store_address1']

                # city
                city = store['store_city']

                # zip
                zipcode = store['store_zip']

                # State
                state = store['state_name']

                # Phone
                phone = store['store_phone'] if store['store_phone'] else '<MISSING>'

                # Lat
                lat = store['store_longitude']

                # Long
                lon = store['store_latitude']

                # Country
                country = 'USA'

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
                self.seen.append(location_id)
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
