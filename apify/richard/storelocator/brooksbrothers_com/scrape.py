import requests

from Scraper import Scrape

URL = "https://www.brooksbrothers.com/"


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
        stores = []

        cookies = {
            'redirection': 'no',
            'Authsite': 'httpss%3A%2F%2Fwww.brooksbrothers.com%2Fon%2Fdemandware.store%2FSites-brooksbrothers-Site%2Fdefault%2FStores-Find%3FICID%3DFind_Store_Top_Option',
            'AppKey': 'NONE',
        }

        headers = {
            'Connection': 'keep-alive',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Origin': 'https://hosted.where2getit.com',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
            'DNT': '1',
            'Content-Type': 'application/json',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Referer': 'https://hosted.where2getit.com/brooksbrothers/?redirection=no',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9,zh-TW;q=0.8,zh;q=0.7',
        }

        # US
        params = (
            ('like', '0.6755496340147362'),
        )
        data = '{"request":{"appkey":"A0540936-B672-11DD-8AA9-A01537ABAA09","formdata":{"geoip":false,"dataview":"store_default","order":"_DISTANCE","limit":20000,"geolocs":{"geoloc":[{"addressline":"90024","country":"US, CA","latitude":"","longitude":""}]},"searchradius":"5000","where":{"country":{"eq":"US"},"or":{"retail":{"eq":""},"redfleececafe":{"eq":""},"redfleece":{"eq":""},"outlet":{"eq":""},"airport":{"eq":""}}},"false":"0"}}}'
        stores.extend(requests.post('https://hosted.where2getit.com/brooksbrothers/rest/locatorsearch', headers=headers, params=params, cookies=cookies, data=data).json()['response']['collection'])

        # Canada
        params = (
            ('like', '0.9752662734468938'),
        )
        data = '{"request":{"appkey":"A0540936-B672-11DD-8AA9-A01537ABAA09","formdata":{"geoip":false,"dataview":"store_default","order":"_DISTANCE","limit":20000,"geolocs":{"geoloc":[{"addressline":"v5e1m2","country":"CA","latitude":"","longitude":""}]},"searchradius":"5000","where":{"country":{"eq":"CA"},"or":{"retail":{"eq":""},"redfleececafe":{"eq":""},"redfleece":{"eq":""},"outlet":{"eq":""},"airport":{"eq":""}}},"false":"0"}}}'
        stores.extend(requests.post('https://hosted.where2getit.com/brooksbrothers/rest/locatorsearch', headers=headers, params=params, cookies=cookies, data=data).json()['response']['collection'])


        for store in stores:
            # Store ID
            location_id = store['uid']

            # Name
            location_title = store['name']

            # Page url
            page_url = '<MISSING>'

            # Type
            location_type = store['storetype']

            # Street
            street_address = store['address1']

            # city
            city = store['city']

            # zip
            zipcode = store['postalcode']

            # State
            state = store['state']
            
            # Province
            province = store['province']

            # Phone
            phone = store['phone']

            # Lat
            lat = store['latitude']

            # Long
            lon = store['longitude']

            # Hour
            hour = ' '.join([
                f"Monday - {store['monopen']} to {store['monclose']}",
                f"Tuesday - {store['tueopen']} to {store['tueclose']}",
                f"Wednesday - {store['wedopen']} to {store['wedclose']}",
                f"Thursday - {store['thuopen']} to {store['thuclose']}",
                f"Friday - {store['friopen']} to {store['friclose']}",
                f"Saturday - {store['satopen']} to {store['satclose']}",
                f"Sunday - {store['sunopen']} to {store['sunclose']}",
            ])

            # Country
            country = store['country']
            
            if country == 'CA':
            	state = province

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
