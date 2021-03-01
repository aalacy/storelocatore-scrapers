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

    locator_domain = "https://www.bhldn.com/"
    base_url = "https://www.bhldn.com/pages/stores"
    r = session.get(base_url)
    soup = bs(r.text, "lxml")
    links = soup.select("ul.secondary-nav__children li.secondary-nav__item a")
    for link in links:
        page_url = urljoin("https://www.bhldn.com", link["href"])
        r1 = session.get(page_url)
        soup1 = bs(r1.text, "lxml")
        store_number = "<MISSING>"
        location_name = soup1.select_one("#store-banner p.title.large").text
        address = [
            _
            for _ in soup1.select_one("#store-banner p.subtitle.pink").stripped_strings
        ]
        street_address = " ".join(address[:-2])
        _split = address[-2].split(",")
        city = _split[0]
        state = _split[1].strip().split(" ")[0]
        zip = _split[1].strip().split(" ")[1]
        country_code = "US"
        phone = address[-1]
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hours = []
        _hours = soup1.select("#store-banner div.flex.horizontal p.day")
        for _ in _hours:
            hours.append(
                f"{_.select_one('.smaller').text}:{_.select_one('.time').text}"
            )

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
