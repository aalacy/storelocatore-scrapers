import requests
import sgzip

from Scraper import Scrape
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('zales_com')



URL = "https://www.zales.com/"


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
        page_urls = []
        stores = []

        cookies = {
            'JSESSIONID': '8528234CDE2FE14470A0652AF873B2B8',
            'ROUTEID': '.node2',
            'AKA_A2': 'A',
            'akaalb_prod-zales': '~op=prod_zales:prod2zales|~rv=4~m=prod2zales:0|~os=1f2f3e33771e07b3045bd0ccbe2c164e~id=6f4ac3e6e2c1cccd27da196a563deb09',
            'bm_sz': '5263A86EB0ADCC416C22AF2102E3F67B~YAAQRbw7F2/RrnduAQAAHgCd4gaKaV21mAK2wHt8vO7gT3pxH+6hXnSb6nmIeHlxIX7gwOsgaeyx2VfOU5a7/iPIeMXKhXBFTy5GybeBC8l62JC39gjaHHNIghVMtjLR2FSXFWnjfyvHqbZFsMh+q6vRTaJ5pilRIW6hMKrTLVMwNARqM9SfZcDGktIm1/4=',
            'AMCVS_700CFDC5570CBFE67F000101%40AdobeOrg': '1',
            'AMCV_700CFDC5570CBFE67F000101%40AdobeOrg': '690614123%7CMCIDTS%7C18238%7CMCMID%7C55906249452249183694569090769834606863%7CMCAAMLH-1576364771%7C9%7CMCAAMB-1576364771%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1575767171s%7CNONE%7CMCAID%7C2E9C880705035FDF-40001195400002FE%7CvVersion%7C3.1.0',
            'mmapi.p.bid': '%22lvsvwcgus11%22',
            'mmapi.p.srv': '%22lvsvwcgus11%22',
            'mm-pc-cartabandon': 'Yes',
            'mm-pc-first-session': '1575759972251',
            '_ga': 'GA1.2.313826018.1575759972',
            '_gid': 'GA1.2.456593216.1575759972',
            'crl8.fpcuid': '0652f1ce-3fa9-4bc9-9936-1268bb5baa2c',
            '_abck': 'E19D6F23E5052AFF92E231A8E96CE845~0~YAAQRbw7F7nRrnduAQAAxgid4gNLYhZZ1wPqjhoqT+hEO86Ch94F6xmjNM66qO52k7QgjbyVXELhyyMYhHmtsHIy2KPNrO0sT5bl7q0paxpy55s11y+Sp0PnlRE8RY49+whAgmWUvG3b6H1VLTZjRS8XEgN2XEEhmSiaMSdiYNsJdpiQVHg+K9HkuG6xTyilS63iONHftt83UPg+jXRBydYNumEDAw3z9Y2Wrvecy7CZV3AuKJMI2h4nbmMUCEngJJP5PBGf/TdcE7XRjzb9ObkWYhpGASpVAkYXrETEPkubz54YpRSOur6LIuPO8GRfj5++r+Bn~-1~-1~-1',
            'aosCookie': 'false',
            's_cc': 'true',
            'ak_bmsc': '2A7FCEEA4538DBFD01B5BFDD603B2E1E173BBC45FB6900006230EC5DA223C255~plmxikTSdBlrXzyVjwF8g5Q6yZmMVL0UA3TTO36SUOfXgzjO+pXO01lDg2Zn/il21vfz3yg0K74LTnmH32d/rERHzS07T3c7l3wHBEMLn3bFz0MJf+pvxv4PZ8DbBX7uEB9Wp0Z1tTwOhknlXlQXN6q4pxqAOa6VaybHNo7PQe3mg/CBG3vnlCBZ1bL5AnyP+0xo6RoZddMrENHAcrfsdpwdrjVVmKG4/Eok6Ajy3ngDoRDrL+fSqKdKAqGFb9utue',
            'gpv_mid': 'anonymous',
            'mmapi.e.AdobeIntegrationCounter': '0',
            'mmapi.e.AdobeIntegrationSvars': '%5B%5D',
            'mmapi.e.AdobeIntegrationSevars': '%5B%5D',
            'mmapi.e.AdobeIntegrationData': '%7B%7D',
            '_scid': 'f93a8481-f45b-45cd-acc8-62996c4c20af',
            'kampyle_userid': '0011-51dd-5ec4-990f-ffe6-0503-bfbf-7f7c',
            'kampyleUserSession': '1575759973918',
            'kampyleUserSessionsCount': '1',
            '_mibhv': 'anon-1575759973941-5890861787_6240',
            '_micpn': 'esp:-1::1575759973941',
            'cd_user_id': '16ee29d0e413cc-0bff757794362f-3964720e-13c680-16ee29d0e42b10',
            'dtm_token': 'AQEIvwTYibS-NgFczv_oAQHssgE',
            '_fbp': 'fb.1.1575759974717.1107689591',
            '_sctr': '1|1575705600000',
            'ORA_FPC': 'id=0307bcc6-b95e-45d6-91e0-c05dff47d7db',
            'WTPERSIST': '',
            'mmapi.p.uat': '%7B%22PayPal%22%3A%22false%22%2C%22TimeFrstSession%22%3A%22Under15%22%2C%22AOS%22%3A%22false%22%2C%22TimeLastSession%22%3A%22Under15%22%7D',
            'mmapi.e.lightbox1564506575833persistData': '%22%7B%5C%22lastShown%5C%22%3A%5C%222019-12-07T23%3A06%3A46.874Z%5C%22%2C%5C%22wasDismissed%5C%22%3Atrue%2C%5C%22displayedCount%5C%22%3A1%7D%22',
            'mmapi.p.pd': '%222128652547%7CBAAAAApVAwAqzbuqcxJVHgABEgABQgBaWe6TAQBJZyw0anvXSP%2F9cg1qe9dIAAAAAP%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FAAZEaXJlY3QBcxIBAAAAAAAAAAAA%2F%2F%2F%2F%2F%2F%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FBACe%2FwAAIid8cetzEgD%2F%2F%2F%2F%2FAXMScxL%2F%2FwQAAAEAAAAAAVZRAgBbgwMAAG4CAQCKbRbDwHMSAP%2F%2F%2F%2F8BcxJzEv%2F%2FBAAAAQAAAAABxlgCAOGQAwAAfgwBAFSEev9acxIA%2F%2F%2F%2F%2FwFzEnMS%2F%2F8EAAABAAAAAAFrcwIAXrUDAACxDgEAbIYMBdNzEgD%2F%2F%2F%2F%2FAXMScxL%2F%2FwQAAAEAAAAAAUd5AgBQvQMAAAMAPv0AAMbW0AAAPvPpAACeAAAAAUU%3D%22',
            'mm-pc-last-session': '1575760036924',
            '_gat': '1',
            'sailthru_pageviews': '3',
            'gpv_pn': 'Find%20a%20Store%20%7C%20Zales%20%7C%20Zales',
            'sailthru_content': '711bb0bef55d473a46b7ffa5cd36afe2914ba64fbf59c7eb806165bba4f0e3de',
            'sailthru_visitor': '760ba3e7-9272-42d0-9d0f-a5f7f3950ce4',
            'kampyleSessionPageCounter': '4',
            '_derived_epik': 'dj0yJnU9R3R0U3hDWmpMOEktWWthWWtKc3ltTnN1VWNrSTNNZG4mbj1GbnlHcWpIcGc2UzZGWlFDdkhvTTR3Jm09NyZ0PUFBQUFBRjNzTUtV',
            'smtrrmkr': '637113568429504971%5E016ee29d-11b1-4bfe-922a-ae9689a742bb%5E016ee29d-11b1-4c33-9efb-7abc714f9536%5E0%5E199.201.64.137',
            'akavpau_prod_zales_vp': '1575760343~id=b540303cfbf81482b4a35860b983afef',
            'bm_sv': '738F05182BBECD9251AF10E64675FBA0~AYISIBf0puvubMy3+toce9nX/TPlsD6iw7lAQMUkttxE0XrIgXG3cqacHiTsPDMWt/y9NCX2J5K7V3kOkXYcyRcgIu2YCCF/LC5/fpFS3+ePOGj0uMh0JfD/fW5spPKV0oYXEnHcza7IbvuGaTabqt3tHwX42kABcdiBjWOyzMU=',
            's_gnr': '1575760049418-New',
            's_sq': 'signetzalesprod%252Csignetglobal%3D%2526c.%2526a.%2526activitymap.%2526page%253DFind%252520a%252520Store%252520%25257C%252520Zales%252520%25257C%252520Zales%2526link%253DFIND%252520STORES%2526region%253DstoreFinderForm%2526pageIDType%253D1%2526.activitymap%2526.a%2526.c%2526pid%253DFind%252520a%252520Store%252520%25257C%252520Zales%252520%25257C%252520Zales%2526pidt%253D1%2526oid%253DFIND%252520STORES%2526oidt%253D3%2526ot%253DSUBMIT',
            'RT': 'z=1&dm=zales.com&si=5f502f49-08af-4222-99b0-cab5877742a0&ss=k3w6su0n&sl=4&tt=6if&bcn=%2F%2F173e2514.akstat.io%2F&ld=1gkj&nu=0d6b495e391be64800350836a95ce62a&cl=1pnh',
        }

        headers = {
            'authority': 'www.zales.com',
            'accept': '*/*',
            'dnt': '1',
            'x-requested-with': 'XMLHttpRequest',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'referer': 'https://www.zales.com/store-finder',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-US,en;q=0.9,zh-TW;q=0.8,zh;q=0.7',
        }

        for zip_search in sgzip.for_radius(50):
            pages = 999
            data = []
            for page in range(0, pages):
                params = (
                    ('q', zip_search),
                    ('page', str(page)),
                )
                res = requests.get('https://www.zales.com/store-finder/find', headers=headers, params=params, cookies=cookies).json()

                if res['total'] == '':
                    break

                data.extend(res['data'])
                if len(data) == res['total']:
                    stores.extend(data)
                    logger.info(f"{res['total']} stores scraped for zipcode {zip_search}")
                    break

        for store in stores:
            if store['name'] not in self.seen:
                # Store ID
                location_id = store['name']

                # Name
                location_title = store['displayName']

                # Page url
                page_url = 'https://www.zales.com' + store['url']

                # Type
                location_type = 'Retail'

                # Street
                street_address = (store['line1'] + ' ' + store['line2']).strip()

                # city
                city = store['town']

                # zip
                zipcode = store['postalCode']

                # State
                state = store['regionIsoCodeShort']

                # Phone
                phone = store['phone']

                # Lat
                lat = store['latitude']

                # Long
                lon = store['longitude']

                # Hour
                hour = '<MISSING>'

                # Country
                country = 'US'

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
