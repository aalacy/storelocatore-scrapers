import json
import requests

from pypostalcode import PostalCodeDatabase
from Scraper import Scrape
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('theshoecompany_ca')



URL = "https://www.theshoecompany.ca"


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

        pcdb = PostalCodeDatabase()
        pc = 'T3Z'
        radius = 3000
        results = pcdb.get_postalcodes_around_radius(pc, radius)
        postalcodes = [p.postalcode for p in results]

        headers = {
            'sec-fetch-mode': 'cors',
            'dnt': '1',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-US,en;q=0.9,zh-TW;q=0.8,zh;q=0.7',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
            'accept': 'application/json, text/plain, */*',
            'referer': 'https://www.theshoecompany.ca/en/ca/',
            'authority': 'www.theshoecompany.ca',
            'cookie': '_abck=5138B76242C076D43B0E17E7386E18F6~-1~YAAQJjPFFxJ43mNtAQAAF7hLewKmnC16vvtSHGOOLvrTkX8cCubc7dXzoGActX45X45QD/sR4udIS1NAs0dKJnXtyL1bDQUzvi3rGtz613uUDnRRGPGLXzj9FyINzjvY+xYi4Y9e2HGpd8WYB2aRDKkP8UTEmTB/NDNik5lLjg5oiHToC2L4Ofl+cKnnJ3DCxdp2PKIVRQoxDeb65iH2JFZvs0BKEYKN0bnUDjBExL2UfcKintYs5vZOqcAeperAgGGX+T+smxdpW8pxCO/BhHLOs5pJU3DpETvr7A==~-1~-1~-1; _evga_3157=f86941228417a184.; TIER=GUEST; BVBRANDID=a11874ba-26e4-4cfb-9ac7-8c841285fb35; cto_lwid=e34e3a00-5596-4f6f-b4bd-287466b4220d; _ga=GA1.2.1668866735.1569731626; AMCVS_6020C2D754D583630A4C98C6%40AdobeOrg=1; s_cc=true; _fbp=fb.1.1569731626165.845940868; s_fid=14386CAE18CC6428-2BD68C5034DC8FF8; bm_sz=2C95705200FC902755A3819754322DBE~YAAQ9zLFF2ORGYNtAQAAEuX9qQW5PDIoTvegnPXDxjunsjMcwurYmRQSwczTN6u0AekdV6tEJCB/wTM6Mkni3JyHqPM1ulr+Z3KRUoSyaOulPpFwxBi190Az2Fhb7BRX8uaQp6uGO1drFPaGxtaPtbU0XhldK5c2XNQIcQAo1rqeycTcPICLR0d+6Rf1WJW4Yx+Do7yGaA==; MOUS=9; ak_bmsc=FC098A1A21F0C57FFC7BD23E557FB94F17C532F77A3000006B289C5D50993271~plNDcvw/71OZUV0IN2QTPu9q9vF4f55haggE64JOtBUu4P2ckeTVzJYM4EExbWdre/9Jn8y4qdOLjLoPkwm8RYbDa8lmGoPstHadzfRw/lTMGGt/Is5wB+UCi9tFJ+i8xtsXIC3k7RgVeCnEbxkpdouqxMQVH9EewrP+EZX1JVCU2vRXxLWcV4QsqMc+RT1qoDmFMlFW8yw6MpZJBRB+uSP38Z57dZg6UJiPuFeiM2qGHYysXj7P7kH8xmzPTBZuvvHh9EzgIXLMrfXSaFzFUWMNhwFcEyUKArZcyN5t44+W4=; JSESSIONID=9QDZOHb8Egr8jnwcvdrfig8U.ATGPS02; _dynSessConf=6057608483931769894; BVBRANDSID=867853f7-45f5-4cca-b958-6a033844947b; _gid=GA1.2.412361150.1570515055; AMCV_6020C2D754D583630A4C98C6%40AdobeOrg=281789898%7CMCIDTS%7C18178%7CMCMID%7C08680147445304652151167050752523131749%7CMCAAMLH-1571119855%7C9%7CMCAAMB-1571119855%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1570522255s%7CNONE%7CMCAID%7CNONE%7CvVersion%7C4.1.0; s_vnum=1572591600299%26vn%3D1; s_invisit=true; aa_lv_s=More%20than%207%20days; bm_sv=12EAE1353D7C724157A2024E4F7BF45D~7RwNnnelQzVDI3VDkMWdjeR6TO8wUiDNyNZ+iSjceDZV+l4LIuRVYD6qjxudB1E2CCPIWUtEZQMoYAqArdlL9zQsQePKe9/U5h0HQvzVFlbciELKX3UiBhsWJL9vYCoZbxWSJpAjoa+y7JEsoep9uvLGqLYbFlDwm2stryGz+q4=; utag_main=v_id:016d7b4bc2d8001b5b728918aa9103078002407000bd0$_sn:2$_ss:0$_st:1570517197917$vapi_domain:theshoecompany.ca$ses_id:1570515054907%3Bexp-session$_pn:1%3Bexp-session$_prevpage:tsc%3Bexp-1570518997921; aa_lv=1570515397928; s_getNewRepeat=1570515397929-Repeat; s_sq=%5B%5BB%5D%5D',
            'sec-fetch-site': 'same-origin',
        }

        for postalcode in postalcodes:
            params = (
                ('address', postalcode.lower()),
                ('distance', '100'),
                ('locale', 'en_CA'),
                ('pushSite', 'TSL_SC'),
                ('sites', 'TSL_SC'),
            )
            r = requests.get('https://www.theshoecompany.ca/api/v1/stores/search', headers=headers, params=params)
            data = json.loads(r.content)['Response']['sortedlist'].values()
            stores.extend(data)
            logger.info(f'{len(data)} locations scraped for postal code {postalcode}')


        for store in stores:
            if store["locationId"] not in self.seen:
                # Store ID
                location_id = store["locationId"]

                # Name
                location_title = store['sites'][0]["description"]

                # Type
                location_type = '<MISSING>'

                # Street
                street_address = store["address1"] + store["address2"] if store["address2"] else store["address1"]

                # State
                state = store["state"]

                # city
                city = store["city"]

                # zip
                zipcode = store["postalCode"]

                # Lat
                lat = store['latitude']

                # Long
                lon = store['longitude']

                # Phone
                phone = store["phoneNumber"]

                # Hour
                hour = store["storeHours"]

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
