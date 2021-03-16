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


def fetch_list(url, data):
    r = session.get(url)
    soup = bs(r.text, "lxml")
    links = soup.select("span.field-content a")
    if links:
        for link in links:
            page_url = urljoin(
                "http://tacotimecanada.com",
                f"{link['href']}",
            )
            fetch_list(page_url, data)
    else:
        fetch_detail(soup, url, data)


def fetch_detail(soup, page_url, data):
    locator_domain = "http://tacotimecanada.com/"
    location_name = soup.select_one("h1#page-title").text.strip()
    store_number = "<MISSING>"
    rows = soup.select("div#block-system-main div.row")
    street_address = ""
    city = ""
    state = ""
    country_code = "CA"
    phone = "<MISSING>"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    location_type = "<MISSING>"
    hours_of_operation = "<MISSING>"
    for row in rows:
        label = row.select_one(".label").text
        if label == "Address:":
            address = [_ for _ in row.select_one(".text").stripped_strings]
            street_address = address[0]
            city = address[1].split(",")[0]
            state = address[1].split(",")[1].strip()
            zip = "<MISSING>"

        if label == "Phone:":
            phone = myutil._valid(row.select_one(".text").text)

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


def fetch_data():
    data = []

    base_url = "http://tacotimecanada.com/locations"
    fetch_list(base_url, data)

    return data


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
