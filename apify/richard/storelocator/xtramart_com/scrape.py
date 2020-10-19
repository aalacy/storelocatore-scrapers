from sgrequests import SgRequests

from Scraper import Scrape

URL = "http://xtramart.com/"


class Scraper(Scrape):
    def __init__(self, url):
        Scrape.__init__(self, url)
        self.data = []
        self.seen = []

    def fetch_data(self):

        session = SgRequests()
        
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

        cookies = {
            'fuel_csrf_token': '97c97019c1368fbf68bd13cc3bd9531e',
            '_ga': 'GA1.2.99190098.1572409103',
            '_gid': 'GA1.2.106771874.1572409103',
            '__atuvc': '2%7C44',
            '__atuvs': '5db90f136653ca7c001',
        }

        headers = {
            'Connection': 'keep-alive',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Origin': 'http://xtramart.com',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36',
            'DNT': '1',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Referer': 'http://xtramart.com/StoreLocator/',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US,en;q=0.9,zh-TW;q=0.8,zh;q=0.7',
        }


        for page_num in range(1,15):
            # print("Page: " + str(page_num))
            data = {
                'latitude': '42.3600825',
                'longitude': '-71.05888010000001',
                'iso2': 'US',
                'cats': '',
                'fuel_csrf_token': '97c97019c1368fbf68bd13cc3bd9531e',
                'page': page_num
            }
            data = session.post('http://xtramart.com/StoreLocator/index.php/api/search/', headers=headers, cookies=cookies, data=data, verify=False).json()['stores']
            stores.extend(data)


        for store in stores:
            if store['id'] not in self.seen:
                # Store ID
                location_id = store['id']

                # Page website
                page_url = '<MISSING>'

                # Type
                location_type = '<MISSING>'

                # Name
                location_title = store['name']

                # Street
                street_address = store['address']

                # city
                city = store['administrative_area_level_2']

                # zip
                zipcode = store['postal_code']

                # State
                state = store['administrative_area_level_1']

                # Phone
                phone = store['phone']

                # Lat
                lat = store['latitude']

                # Long
                lon = store['longitude']

                # Hour
                hour = '<MISSING>'

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
                page_urls.append(page_url)
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
                page_url
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
            page_urls
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
