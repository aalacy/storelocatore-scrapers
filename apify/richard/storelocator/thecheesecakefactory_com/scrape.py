import requests
import sgzip

from xml.etree import cElementTree as ET
from Scraper import Scrape
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('thecheesecakefactory_com')




URL = "https://www.thecheesecakefactory.com"


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
            '_fbp': 'fb.1.1570914063519.2069130573',
        }

        headers = {
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'DNT': '1',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9,zh-TW;q=0.8,zh;q=0.7',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
            'Accept': 'text/javascript, text/html, application/xml, text/xml, */*',
            'X-Prototype-Version': '1.7.2',
            'X-Requested-With': 'XMLHttpRequest',
            'Connection': 'keep-alive',
            'Referer': 'https://hosted.where2getit.com/cheesecake/2014/html/desktop/modules/w2gi_index.html',
        }

        for zip_code in sgzip.for_radius(200):
            params = (
                ('lang', 'fr_FR'),
                ('xml_request', f'<request><appkey>18D36CFE-4EA9-11E6-8D1F-49249CAB76FA</appkey><formdata id="locatorsearch"><dataview>store_default</dataview><geolocs><geoloc><addressline>{zip_code}</addressline><longitude></longitude><latitude></latitude><country>US</country></geoloc></geolocs><searchradius>1000</searchradius><where><or><curbsideflag><eq></eq></curbsideflag><deliveryflag><eq></eq></deliveryflag><doordashflag><eq></eq></doordashflag><banquets><eq></eq></banquets><patio><eq></eq></patio><onlineordering><eq></eq></onlineordering><grubhub><eq></eq></grubhub></or></where><nobf>1</nobf><stateonly>1</stateonly></formdata></request>'),
            )
            response = requests.get('https://hosted.where2getit.com/ajax', headers=headers, params=params, cookies=cookies)
            d = self.etree_to_dict(ET.XML(response.content))
            try:
                data = d['response']['collection']['poi']
            except:
                data = []
            stores.extend(data)
            logger.info(f'{len(data)} locations scraped for {zip_code}')

        for store in stores:
            if isinstance(store, dict) and store['uid'] not in self.seen:
                # Store ID
                location_id = store['uid']

                # Type
                location_type = 'Restaurant'

                # Street
                street_address = store['address1'] + ' ' + store['address2'] if store['address2'] else store['address1']

                # city
                city = store['city']

                # Name
                location_title = f'The Cheesecake Factory - {city}'

                # zip
                zipcode = store['postalcode']

                # State
                state = store['state'] if store['state'] else store['province']

                # Lat
                lat = store['latitude']

                # Long
                lon = store['longitude']

                # Phone
                phone = store['phone']

                # Hour
                hour = ' '.join([str(store['hourslabel1']).replace('None', '') + ": " + str(store['hoursfromto1']).replace('None', ''), str(store['hourslabel2']).replace('None', '') + ": " + str(store['hoursfromto2']).replace('None', ''), str(store['hourslabel3']).replace('None', '') + ": " + str(store['hoursfromto3']).replace('None', ''), str(store['hourslabel4']).replace('None', '') + ": " + str(store['hoursfromto4']).replace('None', '')])

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
                self.seen.append(store['uid'])

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