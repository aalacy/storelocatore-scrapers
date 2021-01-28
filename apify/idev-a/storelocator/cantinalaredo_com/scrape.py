import csv
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests

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
    base_url = "https://www.cantinalaredo.com/locations/"
    r = session.get(base_url)
    soup = bs(r.text, "lxml")
    locations = soup.select("div.wpb_wrapper div.single-location")
    data = []
    for location in locations:
        page_url = "<MISSING>"
        location_name = " ".join(
            [_ for _ in location.select_one(".location-name").stripped_strings]
        )
        address = location.select_one(".location-address").text.split("\\r\\n")
        country_code = address[-1].split(",")[-1]
        city = address[-1].split(",")[0]
        street_address = address[0]
        state = "<MISSING>"
        zip = "<MISSING>"
        phone = myutil._valid(location.select_one(".tel").text)
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        latitude = "<INACCESSIBLE>"
        longitude = "<INACCESSIBLE>"
        hours_of_operation = "; ".join(location.select_one(".hours p").text.split("\n"))

        data.append(
            [
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
        )

    return data


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
