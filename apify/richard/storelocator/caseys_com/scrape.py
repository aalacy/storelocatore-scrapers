import requests

from Scraper import Scrape

URL = "https://www.caseys.com/"


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
        page_urls = []

        cookies = {
            'anonymous-consents': '%5B%5D',
            'cookie-notification': 'NOT_ACCEPTED',
            'JSESSIONID': 'Y24-12c2b2eb-a59f-437d-be38-72ea3264b3cf.accstorefront-8449cbd969-nlgqj',
            'ROUTE': '.accstorefront-8449cbd969-nlgqj',
            'AKA_A2': 'A',
            'rxVisitor': '1575259960041JLK0U3VLR4C4J7H51NBMRKH23K8L1MFE',
            '_gid': 'GA1.2.100132965.1575259961',
            '_gcl_au': '1.1.86527184.1575259962',
            '_gat_UA-38843058-18': '1',
            '_gat_UA-38843058-12': '1',
            '_fbp': 'fb.1.1575259961896.678873847',
            'gig_bootstrap_3_OFr4vtg_Bd96kSUSzSVoxDzFeJ1P64fc157RHIoiHIGKP3YyGUf8Kaak-3GkvqTH': 'ssosocial',
            'dtSa': '-',
            '_ga': 'GA1.1.665743746.1575259961',
            '_ga_BWP94DYDY7': 'GS1.1.1575259961.1.1.1575259963.58',
            'dtPC': '15$259963623_574h-vAHHCHLXXHFFNJNBFNDIPALMLEPHCFAGP',
            'dtLatC': '1',
            'dtCookie': '15$12075FFF155ABD4281E69EDC0D67254B|6574312d70317973|1',
            'rxvt': '1575261769728|1575259960044',
        }

        headers = {
            'authority': 'www.caseys.com',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.87 Safari/537.36',
            'dnt': '1',
            'accept': '*/*',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'referer': 'https://www.caseys.com/store-finder/locations',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-US,en;q=0.9,zh-TW;q=0.8,zh;q=0.7',
        }

        params = (
            ('occasionType', 'carryout'),
            ('address', 'United States'),
            ('latitude', '37.09024'),
            ('longitude', '-95.71289100000001'),
        )

        stores = requests.get('https://www.caseys.com/store-finder/getStores', headers=headers, params=params, cookies=cookies).json()['stores']

        for store in stores:
            # Store ID
            location_id = store['name']

            # Name
            location_title = store['displayName']

            # Page url
            page_url = store['url']

            # Type
            location_type = 'Restaurant'

            # Street
            street_address = store['address']['line1']

            # city
            city = store['address']['town']

            # zip
            zipcode = store['address']['postalCode']

            # State
            state = store['address']['region']['isocodeShort']

            # Phone
            phone = store['address']['phone']

            # Lat
            lat = store['latitude']

            # Long
            lon = store['longitude']

            hour_list = []
            if location_id == '1814':
                for hour_type in store['openingHours']['weekDayOpeningList'][2:]:
                    if hour_type['hourType'] == 'STOREOPEN':
                        hour_list.append(', '.join(hour_type['daysList']) + ": " + hour_type['openingTime']['formattedHour'] + ' - ' + hour_type['closingTime']['formattedHour'])
            else:
                for hour_type in store['openingHours']['weekDayOpeningList']:
                    if hour_type['hourType'] == 'STOREOPEN':
                        hour_list.append(', '.join(hour_type['daysList']) + ": " + hour_type['openingTime']['formattedHour'] + ' - ' + hour_type['closingTime']['formattedHour'])

            # Hour
            hour = ' '.join([day for day in hour_list])

            # Country
            country = store['address']['country']['isocode']

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
