import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from urllib.parse import urljoin

from util import Util  # noqa: I900

myutil = Util()


session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
        writer.writerow(
            [
                "locator_domain",
                "page_url",
                "location_name",
                "street_address",
                "city",
                "state",
                "zip",
                "country_code",
                "store_number",
                "phone",
                "location_type",
                "latitude",
                "longitude",
                "hours_of_operation",
            ]
        )
        # Body
        for row in data:
            writer.writerow(row)


def _headers():
    return {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Language": "en-US,en;q=0.9,ko;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://www.beaverbrooks.co.uk/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36",
    }


def _data():
    return {
        "countryCode": "CA",
        "latitude": "43.653226",
        "longitude": "-79.3831843",
        "locale": "en_CA",
        "limit": 1500,
        "radius": 80000,
        "type": "",
    }


def fetch_data():
    data = []

    locator_domain = "https://www.beaverbrooks.co.uk/"
    base_url = "https://www.beaverbrooks.co.uk/stores"
    rr = session.get(base_url, headers=_headers())
    soup = bs(rr.text, "lxml")
    locations = soup.select("ul.stores-list li.stores-list__store")
    for location in locations:
        page_url = urljoin(
            "https://www.beaverbrooks.co.uk", location["data-store-link"].strip()
        )
        r1 = session.get(page_url)
        soup1 = bs(r1.text, "lxml")
        store_number = "<MISSING>"
        location_name = ""
        country_code = "UK"
        state = "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = "<MISSING>"
        latitude = location["data-lat"]
        longitude = location["data-long"]
        hours_of_operation = "<MISSING>"
        street_address = "<MISSING>"
        city = "<MISSING>"
        zip = "<MISSING>"
        phone = "<MISSING>"
        try:
            location_name = soup1.select_one('h1[itemprop="name"]').text
            street_address = soup1.select_one(
                'p.header-address span[itemprop="streetAddress"]'
            ).text.strip()[:-1]
            city = soup1.select_one("p.header-address span").text.replace(",", "")
            zip = soup1.select_one(
                'p.header-address span[itemprop="postalCode"]'
            ).text.strip()
            phone = myutil._valid(
                soup1.select_one(
                    'div.store-details-page__details-phone p[itemprop="telephone"]'
                ).text
            )
            hours = []
            for _ in soup1.select("table.store-openings.weekday-openings tr"):
                day = _.select_one(".weekday-openings__day").text
                opens = _.select_one('[itemprop="opens"]').text.strip()
                closes = _.select_one('[itemprop="closes"]').text.strip()
                if opens and closes:
                    hours.append(f"{day} {opens}-{closes}")
                else:
                    hours.append(
                        f'{day} {_.select_one(".weekday-openings__times").text.strip()}'
                    )

            hours_of_operation = myutil._valid("; ".join(hours))
        except:
            location_name = soup1.select_one("h1").text
            location_type = "Closed"

        _item = [
            locator_domain,
            page_url,
            location_name,
            street_address,
            city,
            state,
            zip,
            country_code,
            store_number,
            phone,
            location_type,
            latitude,
            longitude,
            hours_of_operation,
        ]

        myutil._check_duplicate_by_loc(data, _item)
    return data


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
