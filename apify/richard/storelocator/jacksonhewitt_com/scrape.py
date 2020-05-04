import json

import requests
import sgzip
from Scraper import Scrape
import time

URL = "https://www.jacksonhewitt.com"


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
        stores = []
        urls = []
        seen = []

        cookies = {
            "__cfduid": "d27b3af318d78fa44369b8a3ff0eb74541570304881",
            "ASP.NET_SessionId": "udprtlqwyubdtueja05hhvrg",
            "ARRAffinity": "b842d7a63437b37059c463f780d5f34012a9c52ffc8265c65d6daa7cf098a52f",
            "visid_incap_410416": "vOu8eX9NSmSx9hv50yoch3HzmF0AAAAAQUIPAAAAAABxiTg+10wP4OdQFjCN0KCu",
            "nlbi_410416": "lemjc0kqvwdnLid0MVdxAAAAAACKXtnZKv69DDLeFLSnXm+D",
            "incap_ses_228_410416": "tsK+RzzV5B4s3184dwYqA3LzmF0AAAAAwdLxpCRIyDnJ0YM2jtD0sQ==",
            "ai_user": "9PMfw|2019-10-05T19:48:03.124Z",
            "_gcl_au": "1.1.1865734202.1570304883",
            "initialTrafficSource": "utmcsr=(direct)|utmcmd=(none)|utmccn=(not set)",
            "__utmzzses": "1",
            "_ga": "GA1.2.648976758.1570304883",
            "_gid": "GA1.2.1818589494.1570304883",
            "_dc_gtm_UA-9915297-12": "1",
            "BCSessionID": "6dee6bd5-f3e1-4ae7-9dd2-a3687aba2312",
            "_fbp": "fb.1.1570304883481.283033281",
            "gwcc": "%7B%22fallback%22%3A%228558764549%22%2C%22clabel%22%3A%22AbM-CO_VuqcBEI2n7NYC%22%2C%22backoff%22%3A86400%2C%22backoff_expires%22%3A1570391283%7D",
            "__qca": "P0-1606149338-1570304883624",
            "kw_fwABAVu7bX9PmQDE": "648976758.1570304883",
            "_gat_UA-9915297-12": "1",
            "jhafc": "bb74007ec42145ef89741b4e94b41220&SameSite=Strict",
            "ai_session": "/MCTW|1570304883586|1570304893170.335",
            "_derived_epik": "dj0yJnU9dGRXV3FtUTA0UkZHV05SaFk0eXQwbWVVa1RUNktabFAmbj1WTEVRWlY2MWZ2SDVoTjdwN0w2SldRJm09NyZ0PUFBQUFBRjJZODMw",
            "_tq_id.TV-81729009-1.83e6": "32c3815a50032dfb.1570304884.0.1570304894..",
        }

        headers = {
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "DNT": "1",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9,zh-TW;q=0.8,zh;q=0.7",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36",
            "Accept": "*/*",
            "Referer": "https://www.jacksonhewitt.com/officelocator/?search=94587&filterWallmart=false&filterOpenAllYear=true&filterSpanishSpeaking=false&filterRefundAdvance=false&filterTaxCourses=false",
            "X-Requested-With": "XMLHttpRequest",
            "Connection": "keep-alive",
            "Request-Id": "|GCiK0.bTkAJ",
            "jhafst": "bb74007ec42145ef89741b4e94b41220",
            "Request-Context": "appId=cid-v1:66f283fb-f002-4eef-8768-79c17a1f335a",
        }

        for zipcode in sgzip.for_radius(50):
            response = requests.get(
                f"https://www.jacksonhewitt.com/api/offices/search/{zipcode}",
                headers=headers,
                cookies=cookies,
            )
            try:
                data = json.loads(response.content)["Offices"]
            except:
                print('sleeeeeping..............\n\n\n\n\n\n\n\n\n')
                time.sleep(60)
                response = requests.get(
                    f"https://www.jacksonhewitt.com/api/offices/search/{zipcode}",
                    headers=headers,
                    cookies=cookies,
                )
                data = json.loads(response.content)["Offices"]

            stores.extend(data)
            print(f"{len(data)} of locations scraped for zipcode: {zipcode}")

        for store in stores:
            if store["OfficeNumber"] not in seen:
                # Store ID

                location_id = store["OfficeNumber"]

                # Name
                location_title = "Hackson Hewitt" + " " + store["City"]

                # Type
                location_type = store["TypeName"].strip()

                if location_type == '':
                    location_type = '<MISSING>'

                # Street
                street_address = store["Address1"] + store["Address2"]

                # Country
                country = "US"

                # State
                state = store["State"]

                # city
                city = store["City"]

                # zip
                zipcode = store["ZipCode"]

                # Lat
                lat = store["Latitude"]

                # Long
                lon = store["Longitude"]

                # Phone
                phone = store["Phone"]

                # hour
                hour_arr = store["OfficeHours"]
                hour = ''
                for h in hour_arr:
                    hour += h['DayOfWeek'] + ' ' + h['Hours'] + ' '

                hour = hour.strip()


                url = 'https://www.jacksonhewitt.com/' + store['DetailsUrl']

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
                urls.append(url)
                seen.append(location_id)

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
            url
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
            urls
        ):
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
                    url
                ]
            )


scrape = Scraper(URL)
scrape.scrape()
