import csv
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
import re

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
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        # 'accept-encoding': 'gzip, deflate, br',
        "accept-language": "en-US,en;q=0.9,ko;q=0.8",
        "referer": "https://veggiegrill.com/",
        "cache-control": "max-age=0",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "same-origin",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
    }


def fetch_data():
    start_url = "https://veggiegrill.com/"
    session.get(start_url, headers=_headers())
    base_url = "https://veggiegrill.com/locations/"
    r = session.get(base_url, headers=_headers())
    soup = bs(r.text, "html.parser")
    locations = soup.select("div.accordions .location-sm")
    data = []
    for location in locations:
        store_number = location["id"]
        location_name = location.select_one("b").text
        address = [_ for _ in location.select_one("address").stripped_strings]
        street_address = address[0]
        city = myutil._valid(address[1].split(",")[0])
        state = address[1].split(",")[1].strip().split(" ")[0]
        zip = address[1].split(",")[1].strip().split(" ")[1]
        country_code = myutil.get_country_by_code(state)
        phone = myutil._valid(
            location.find("a", string=re.compile("\\d{3}-\\d{4}")).text
        )
        link = soup.find("div", attrs={"data-id": store_number})
        page_url = link.a["href"]
        r1 = session.get(page_url, headers=_headers())
        soup1 = bs(r1.text, "lxml")
        location_type = "<MISSING>"
        latitude = "<INACCESSIBLE>"
        longitude = "<INACCESSIBLE>"
        labels = [_.text for _ in soup1.select("dl.hours dt")]
        values = [_.text.strip() for _ in soup1.select("dl.hours dd")]
        hours = []
        for x in range(len(labels)):
            hours.append(f"{labels[x]}: {values[x]}")
        hours_of_operation = "; ".join(hours)

        _item = [
            base_url,
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
