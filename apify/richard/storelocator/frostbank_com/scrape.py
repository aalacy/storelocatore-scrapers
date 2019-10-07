import requests
import json
import sgzip

from Scraper import Scrape

URL = "https://www.frostbank.com"


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
            'NEW_VISITOR': 'new',
            'VISITOR': 'returning',
            'TLTSID': '48CF52CEE27B10E207EBFA2EF7B862CC',
            'TLTUID': '48CF52CEE27B10E207EBFA2EF7B862CC',
            '_gcl_au': '1.1.1614181351.1569735473',
            'session_alive': '1',
            '_ga': 'GA1.2.3611815.1569735473',
            '_gid': 'GA1.2.1809512312.1569735473',
            '_fbp': 'fb.1.1569735473316.537318747',
            'JSESSIONID': 'dVl7-HPcuttf2BGsc1-cS4W9WXIa1MWjmf9MWSeO.puba1:public_node_a1',
        }

        headers = {
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Origin': 'https://www.frostbank.com',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9,zh-TW;q=0.8,zh;q=0.7',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
            'Content-Type': 'application/json;charset=UTF-8',
            'Accept': 'application/json, text/plain, */*',
            'Referer': 'https://www.frostbank.com/locations?lq=78205',
            'Connection': 'keep-alive',
            'DNT': '1',
        }

        for zip_search in sgzip.for_radius(50):
            if zip_search[0] == '7':
                data = '{"searchKeyword"' + f':"{zip_search}"' + ', "distance":10}'
                response = requests.post('https://www.frostbank.com/.rest/public/locations/v1/location/searchbykeyword', headers=headers, cookies=cookies, data=data)
                try:
                    data = json.loads(response.text)['locations']
                    stores.extend(json.loads(response.text)['locations'])
                    print(f'{len(data)} locations scraped for zipcode {zip_search}')
                except:
                    print(f'0 location scraped for zipcode {zip_search}')
                    pass

        for store in stores:
            if store['id'] not in self.seen:
                # Store ID
                location_id = store['id']

                # Name
                location_title = store['name']

                # Type
                location_type = store['branchType']

                # Street
                street_address = store['address1']

                # city
                city = store['city']

                # zip
                zipcode = store['zip']

                # State
                state = store['state']

                # Lat
                lat = store['latitude']

                # Long
                lon = store['longitude']

                # Phone
                phone = store['phone']

                # Hour
                if len(''.join([store['lobbyHoursMonToThu'], store['lobbyHoursFri'], store['lobbyHoursSat'], store['atmHours']]).strip()) == 0:
                    hour = '<MISSING>'
                else:
                    hour = ' '.join(['lobby Hours Mon To Thu:' + store['lobbyHoursMonToThu'], 'lobby Hours Fri:' + store['lobbyHoursFri'], 'lobby Hours Sat:' + store['lobbyHoursSat'], 'atm Hours:' + store['atmHours']])

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
