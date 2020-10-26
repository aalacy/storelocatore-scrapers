import requests
import sgzip

from Scraper import Scrape
from uszipcode import SearchEngine
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('claires_com')



URL = "https://www.claires.com/"


class Scraper(Scrape):
    def __init__(self, url):
        Scrape.__init__(self, url)
        self.data = []
        self.seen = []
        self.search = SearchEngine(simple_zipcode=True)

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
            'authority': 'www.claires.com',
            'accept': '*/*',
            'origin': 'https://www.claires.com',
            'x-requested-with': 'XMLHttpRequest',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.87 Safari/537.36',
            'dnt': '1',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'referer': 'https://www.claires.com/us/store-locator/',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-US,en;q=0.9,zh-TW;q=0.8,zh;q=0.7',
            '$cookie': '__cfduid=de096103334a1c95deb03d130ac08f4cc1575262810; dwsid=bkIvar97ULkzOyExvL0rcQK1cXnQKEzDXQSWOzMkPnk6F1k4V6TpKLmzehrkwkVuV70_hLbdMSNubRo4X1HrIw==; dwac_fd255e698c6e5985a49c555b27=fCIb8HJO7AITgQ0gyS7PURDVReMdHfB4fb4%3D|dw-only|||GBP|false|Etc%2FUTC|true; dwsecuretoken_7f375bc57c52b03dc0b1dcf10243baa2=OZUDRXk34T9glIAP7MEIUSOG5rFFCyn0Wg==; sid=fCIb8HJO7AITgQ0gyS7PURDVReMdHfB4fb4; dwanonymous_7f375bc57c52b03dc0b1dcf10243baa2=abQKDLqf4Mbbsa8gErvvjtzoKl; dwac_7ff94a19027a7190d53f769d85=fCIb8HJO7AITgQ0gyS7PURDVReMdHfB4fb4%3D|dw-only|||USD|false|Etc%2FUTC|true; cqcid=abDLF0VVXKxPEUxK1Je2ASFlxH; dwsecuretoken_f4b17e7f229ed2185a9cb01466336095=gjcfYyMTW-52TE2hfx2GpbHsZwonxLNIkg==; dwanonymous_f4b17e7f229ed2185a9cb01466336095=abDLF0VVXKxPEUxK1Je2ASFlxH; __cq_dnt=0; dw_dnt=0; _ga=GA1.2.230133618.1575262813; _gid=GA1.2.500622625.1575262813; _gcl_au=1.1.944517434.1575262813; FirstSession=source%3Ddirect%26medium%3Dnone%26campaign%3Ddirect%26term%3D%26content%3D%26date%3D20191202; dw=1; dw_cookies_accepted=1; dw_TLSWarning=false; _dc_gtm_UA-48487400-7=1; _gat_UA-48487400-7=1; _scid=8eebdedd-5b48-4ec4-a427-9adaec22c296; _hjid=24cbf760-9c78-4eb7-80d7-839878f12e9e; _sctr=1|1575187200000; __cq_uuid=a024bce0-14c0-11ea-ba0c-4f80e3ecca96; __cq_seg=0~0.00\\u00211~0.00\\u00212~0.00\\u00213~0.00\\u00214~0.00\\u00215~0.00\\u00216~0.00\\u00217~0.00\\u00218~0.00\\u00219~0.00; cto_lwid=f7165b84-22ba-4bd4-9586-20e26a70b4f2; _fbp=fb.1.1575262814479.983479264; _derived_epik=dj0yJnU9NjdXeXg5bVVDSWdRemF0X19MMWxtOFJQczlIVGhtTkYmbj1rYkRBcHNRTEItWlFRM1M2R0R1eE9nJm09NyZ0PUFBQUFBRjNrbW1n; uuid=0d325831d7774f9e95ac1c53747d0c4e',
        }

        for coords in sgzip.coords_for_radius(50):
            data = {
                'time': '12:00',
                'page': 'storelocator',
                'lat': coords[0],
                'lng': coords[1]
            }
            data = requests.post('https://www.claires.com/on/demandware.store/Sites-clairesNA-Site/en_US/Stores-GetNearestStores', headers=headers, data=data).json()['stores']
            stores.extend(data)
            logger.info(f"{len(data)} locations scraped for coords: {coords[0]}, {coords[1]}")

        for store in stores:
            if store['id'] not in self.seen:
                # Store ID
                location_id = store['id']

                # Name
                location_title = store['name']

                # Page url
                page_url = '<MISSING>'

                # Type
                location_type = 'Retail'

                # Street
                street_address = store['address1']

                # city
                city = store['city']

                # zip
                zipcode = store['postalCode']

                # State
                state = self.search.by_zipcode(zipcode).state

                # Phone
                phone = store['phone']

                # Lat
                lat = store['coordinates']['lat']

                # Long
                lon = store['coordinates']['lng']

                # Hour
                hour = ' '.join([f"{hour['day']}: {hour['from']} to {hour['to']}" for hour in store['storeHours']])

                # Country
                country = store['country']

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
