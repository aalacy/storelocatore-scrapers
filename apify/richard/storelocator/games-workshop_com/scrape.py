import requests
import json
import sgzip

from Scraper import Scrape


URL = "https://www.games-workshop.com/"


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
        store_type_list = []
        states = []
        zip_codes = []
        latitude_list = []
        longitude_list = []
        phone_numbers = []
        hours = []
        countries = []
        stores = []
        seen = []

        headers = {
            'accept': 'application/json',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-US,en;q=0.9,zh-TW;q=0.8,zh;q=0.7',
            'cookie': '__cfduid=d2b5d278d067e8b91ff92701b2f00885f1567275666; BIGipServeratg-prod-gwgp_oracleoutsourcing_com_http=3484176513.52747.0000; previous_session=true; _ga=GA1.2.196791888.1567275809; _fbp=fb.1.1567275810168.335265528; sc.ASP.NET_SESSIONID=xnbeiahoaba3zwefxhsv4ylq; gw-location=en_US_gw; cookieWarning_gw=1; __cf_bm=ba684abc0399c2d2ff4a6482dd9207012d4de71a-1568160886-1800-Ad2D33zWcamp0NDEZp/bFRYuQWcmRmlwwb9uKshp5h3vQLuEQDjnmSL2L3AgF0fa0W6nvw23ogIpGDb7F0hBv6Y=; JSESSIONID=fFUdrC4B6HHpAsPbQbjQNwoW43yWTTtfbCS2i7c5n9YnJFiLDDWjGGmWRk6Lom6k9Cz6LkK9ltSxTPxAteB-wepxD-UZh7QIwDevLchdnTVyhX3J46x7pkbcLLxSJboF!1058472226; _gid=GA1.2.1926711881.1568160887; _gaexp=GAX1.2.2KOSY47QQm2_WvAP-8ipqA.18237.0; _gat_UA-5285490-1=1',
            'dnt': '1',
            'referer': 'https://www.games-workshop.com/en-US/store/storefinder.jsp',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
            'x-newrelic-id': 'VwAPVVNQGwIEXVZUBQcD',
            'x-requested-with': 'XMLHttpRequest',
        }

        for coord in sgzip.coords_for_radius(100):
            r = requests.get(
                url=f'https://www.games-workshop.com/en-US/store/fragments/resultsJSON.jsp?latitude={coord[0]}&radius=100&longitude={coord[1]}',
                headers=headers
            )
            stores.extend(json.loads(r.content)['locations'])



        for store in stores:
            if store['type'] != 'independentRetailer':
                # Store ID
                location_id = store['storeId'] if 'storeId' in store.keys() else '<MISSING>'

                # Name
                location_title = store["name"] if 'name' in store.keys() else '<MISSING>'

                # Street
                street_address = store['address1'] if 'address1' in store.keys() else '<MISSING>'

                # Country
                country = store['country'] if 'country' in store.keys() else '<MISSING>'

                # State
                state = store['state'] if 'state' in store.keys() else '<MISSING>'

                # city
                city = store['city'] if 'city' in store.keys() else '<MISSING>'

                # zip
                zipcode = store['postalCode'] if 'postalCode' in store.keys() else '<MISSING>'

                # store type
                store_type = store['type'] if 'type' in store.keys() else '<MISSING>'

                # Lat
                lat = store['latitude'] if 'latitude' in store.keys() else '<MISSING>'

                # Long
                lon = store['longitude'] if 'longitude' in store.keys() else '<MISSING>'

                # Phone
                phone = store['telephone'] if 'telephone' in store.keys() else '<MISSING>'

                # hour
                hour = '<MISSING>'

                # Store data
                locations_ids.append(location_id)
                store_type_list.append(store_type)
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
                store_type
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
            store_type_list
        ):
            if location_id not in seen:
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
                        store_type,
                        latitude,
                        longitude,
                        hour,
                    ]
                )
                seen.append(location_id)



scrape = Scraper(URL)
scrape.scrape()
