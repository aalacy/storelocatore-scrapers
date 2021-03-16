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


def fetch_data():
    data = []

    locator_domain = "https://www.citymattress.com/"
    base_url = "https://www.citymattress.com/pages/stores"
    r = session.get(base_url)
    soup = bs(r.text, "lxml")
    locations = soup.select(".store-items article.store-item")
    for location in locations:
        page_url = urljoin(
            "https://www.citymattress.com",
            location.select_one("a.store-item__title")["href"],
        )
        location_name = location.select_one(
            "h2.store-item__title a.store-item__title"
        ).text.strip()
        address = [
            _.strip()
            for _ in location.select_one(".store-item__address").stripped_strings
        ]
        street_address = " ".join(address[:-1])
        city = address[-1].split(",")[0]
        state = address[-1].split(",")[1].strip().split(" ")[0]
        zip = address[-1].split(",")[1].strip().split(" ")[1]
        country_code = "US"
        phone = myutil._valid(location.select_one(".store-item__phone a").text)
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        latitude = location["data-lat"]
        longitude = location["data-lng"]
        hours = [
            _
            for _ in location.select_one(".store-item__hours").text.split("\n")
            if _.strip()
            and _.strip() != "Book An Appointment"
            and _.strip() != "GRAND OPENING"
        ]
        hours_of_operation = myutil._valid("; ".join(hours))

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

        data.append(_item)

    return data


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
