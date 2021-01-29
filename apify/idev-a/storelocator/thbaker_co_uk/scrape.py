import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs

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
    base_url = "https://www.thbaker.co.uk/stores/"
    r = session.get(base_url)
    soup = bs(r.text, "lxml")
    links = soup.select("div.amlocator-store-desc a.amlocator-link")
    data = []
    for link in links:
        page_url = link["href"]
        r1 = session.get(page_url)
        soup1 = bs(r1.text, "lxml")
        location_name = soup1.h1.string
        address = myutil._strip_list(
            [
                _
                for _ in soup1.select_one(
                    "div.amlocator-block.amlocator-location-info p"
                ).stripped_strings
            ]
        )
        address = address[1:]  # remove title
        country_code = "UK"
        zip = address[-1]
        city = address[-2]
        state = "<MISSING>"
        street_address = " ".join(address[:-2])
        phone = soup1.select_one("div.amlocator-block.-contact a").string
        phone = phone.replace("Tel:", "").strip()
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        direction = myutil._strip_list(
            r1.text.split("locationData: {")[1]
            .strip()
            .split("marker_url: ''")[0]
            .split(",")
        )
        latitude = direction[0].replace("lat:", "").strip()
        longitude = direction[1].replace("lng:", "").strip()
        rows = soup1.select("div.amlocator-schedule-table div.amlocator-row")
        hours = []
        for row in rows:
            hours.append(f"{row.findChildren()[0].text}: {row.findChildren()[1].text}")
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
        myutil._check_duplicate_by_loc(data, _item)

    return data


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
