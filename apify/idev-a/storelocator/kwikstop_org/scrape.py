import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from urllib.parse import urljoin
import json

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

    locator_domain = "https://www.kwikstop.org/"
    base_url = "https://www.kwikstop.org/locations"
    r = session.get(base_url)
    soup = bs(r.text, "lxml")
    links = soup.select("#page .row.sqs-row a")
    for link in links:
        page_url = urljoin(
            "https://www.kwikstop.org",
            f"{link['href']}",
        )
        r1 = session.get(page_url)
        soup1 = bs(r1.text, "lxml")
        rows = soup1.select("#page .row.sqs-row .row.sqs-row")
        for row in rows:
            location = row.select_one(".sqs-block-map")
            if location:
                try:
                    location1 = [
                        _ for _ in row.select_one(".sqs-block-html").stripped_strings
                    ]
                    block = json.loads(location["data-block-json"])["location"]
                    location_name = location1[0].split("#")[0].strip()
                    store_number = location1[0].split("#")[1].strip()
                    street_address = location1[1]
                    address = location1[2].split(",")
                    city = address[0]
                    state = ""
                    zip = ""
                    if len(address) == 2:
                        state = (
                            address[1].strip().split(" ")[0].replace(".", "").strip()
                        )
                        zip = address[1].strip().split(" ")[1].replace(",", "").strip()
                    else:
                        zip = address[-1].strip().replace(".", "").strip()
                        state = address[1].strip().replace(",", "").strip()

                    country_code = "US"
                    phone = myutil._valid(location1[-1])
                    location_type = "<MISSING>"
                    latitude = block["mapLat"]
                    longitude = block["mapLng"]
                    hours_of_operation = "<MISSING>"

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
                except Exception as err:
                    print(err)
                    import pdb

                    pdb.set_trace()
    return data


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
