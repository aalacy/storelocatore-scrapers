import json

import requests
import sgzip
from Scraper import Scrape


URL = "celine.com"


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
        stores = []
        seen = []

        headers = {
            "accept": "application/json",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "en-US,en;q=0.9,zh-TW;q=0.8,zh;q=0.7",
            "cookie": "__cfduid=d24a4ef0dd2121b660960ab850eea8bcb1567440380; _gcl_au=1.1.392025716.1567440401; cartItemNumber=0; _ga=GA1.2.452346534.1567440401; _abck=D8754B70249CED827066BD13FB403EB8~0~YAAQFUsHYPpJLdRsAQAA3nO68gIT7Poxr1V/mTKq8mkAR86OyEvVmzgU2dwO8vtzccBxocoDbKNKJs1aZZAfs1dEOVmJQYu/dnTovteAifYKlfppDwMsN0WwPMrkqoKeBmrP4dHMbg+rZruQQUmAdtQgXNxyB1u/Z5tHW538LJg6dHwnWX50pjlRzOQRiRcku7BVQOXku96mEQvgR/BMbakFdRWfulllGLG+OL0X2eqTYb1bR+lKrs9JG48dy87K6eFHSA8UFqr29zqJtEAEnBb2LAi8qUnhXfOzZncwzDL57XPKjPE34js=~-1~-1~-1; _fbp=fb.1.1567440405945.1384358145; __utmc=199958332; __utmz=199958332.1567440412.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); _ga=GA1.3.452346534.1567440401; __utma=199958332.452346534.1567440401.1567831619.1568041277.3; _gid=GA1.3.1297343513.1568158533; _gat_UA-12251584-6=1",
            "dnt": "1",
            "referer": "https://stores.celine.com/en_us/home?c=US&q=",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36",
        }
        r = requests.get(
            url="https://stores.celine.com/en_us/home?offset=50&c=US&q=",
            headers=headers,
        )
        stores.extend(json.loads(r.content)["response"]["entities"])

        for store in stores:

            # Store ID
            location_id = store["profile"]["meta"]["id"]

            # Name
            location_title = store["profile"]["name"]

            # Street
            street_address = (
                store["profile"]["address"]["line1"]
                + " "
                + store["profile"]["address"]["line2"]
                if store["profile"]["address"]["line2"]
                else store["profile"]["address"]["line1"]
            )

            # Country
            country = store["profile"]["address"]["countryCode"]

            # State
            state = store["profile"]["address"]["region"]

            # city
            city = store["profile"]["address"]["city"]

            # zip
            zipcode = store["profile"]["address"]["postalCode"]

            # Lat
            lat = store["profile"]["yextDisplayCoordinate"]["lat"]

            # Long
            lon = store["profile"]["yextDisplayCoordinate"]["long"]

            # Phone
            phone = store["profile"]["mainPhone"]["display"]

            # hour
            hour = (
                store["profile"]["hours"]
                if "hours" in store["profile"].keys()
                else "<MISSING>"
            )

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
                        "<MISSING>",
                        latitude,
                        longitude,
                        hour,
                    ]
                )
                seen.append(location_id)


scrape = Scraper(URL)
scrape.scrape()
