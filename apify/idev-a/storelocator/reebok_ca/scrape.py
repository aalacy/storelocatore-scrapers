import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
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

    locator_domain = "https://www.reebok.ca/"
    base_url = "https://reebokstorelocator.ca/"
    rr = session.get(base_url)
    soup = bs(rr.text, "lxml")
    locations = json.loads(
        [_.contents[0] for _ in soup.select("script") if _.contents][0]
        .split("locations = ")[1]
        .strip()
        .split("content = ")[0]
        .strip()[:-1]
    )
    for id in locations:
        store_number = id
        location = locations[id]
        location_name = location["full_name"]
        country_code = "CA"
        page_url = "<MISSING>"
        address = [_ for _ in bs(location["address"], "lxml").stripped_strings]
        city = ""
        state = ""
        zip = ""
        street_address = ""
        if len(address) == 2:
            street_address = address[0]
            city = address[-1].split(",")[0]
            state = address[-1].split(",")[1].strip()
            zip = address[-1].split(",")[2].strip()
        else:
            street_address = " ".join(address[:-2])
            city = address[-2].split(",")[0]
            state = address[-2].split(",")[1].strip()
            zip = address[-1]

        state = state.encode("unicode-escape").decode("utf8").replace("\\xe9", "e")
        phone = myutil._valid(location["phone"])
        location_type = "<MISSING>"
        latitude = location["lat"]
        longitude = location["lng"]
        hours_of_operation = myutil._valid(
            "; ".join(
                myutil._strip_list(
                    [_ for _ in bs(location["hours"], "lxml").stripped_strings]
                )[1:]
            )
        )

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
