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


def _phone(phone):
    if phone:
        return phone.split("\n")[0].strip().replace("Phone:", "")
    else:
        return "<MISSING>"


def fetch_data():
    data = []

    locator_domain = "https://martins-supermarkets.com/"
    base_url = "https://martins-supermarkets.com/stores"
    rr = session.get(base_url)
    soup = bs(rr.text, "lxml")
    locations = soup.select("div.isotope a")
    for location in locations:
        page_url = urljoin(locator_domain, location.get("href"))
        store_number = "<MISSING>"
        location_name = myutil._valid(location.h3.text)
        country_code = "US"
        block = [_ for _ in location.h4.stripped_strings]
        street_address = " ".join(block[:-2])
        city = block[-2].split(",")[0]
        state = block[-2].split(",")[1].strip().split(" ")[0]
        zip = block[-2].split(",")[1].strip().split(" ")[1]
        phone = block[-1]
        location_type = "<MISSING>"
        r1 = session.get(page_url)
        soup1 = bs(r1.text, "lxml")
        latitude = soup1.marker["lat"]
        longitude = soup1.marker["lng"]
        text1 = [
            _
            for _ in soup1.select_one(
                "section.container div.text div.row div.col-sm-6"
            ).stripped_strings
        ]
        hours_of_operation = "<MISSING>"
        for _ in text1:
            if _.startswith("Store Hours:"):
                hours_of_operation = _.replace("Store Hours:", "").strip()
                break

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
