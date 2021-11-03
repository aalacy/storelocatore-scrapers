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


def _headers():
    return {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accept-language": "en-US,en;q=0.9,ko;q=0.8",
        "referer": "https://stores.burton.co.uk/index.html",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36",
    }


def parse_detail(page_url, data):
    locator_domain = "https://www.burton.co.uk/"
    r1 = session.get(page_url, headers=_headers())
    soup1 = bs(r1.text, "lxml")
    sub_links = soup1.select(".Directory-content .Teaser-titleLink")
    if sub_links:
        for link in sub_links:
            page_url = urljoin("https://stores.burton.co.uk/", link["href"])
            parse_detail(page_url, data)
    else:
        store_number = "<MISSING>"
        location_type = soup1.select_one("#location-name .Hero-brand").text
        location_name = soup1.select_one("#location-name .Hero-geo").text
        city = soup1.select_one('#address meta[itemprop="addressLocality"]')["content"]
        _state = soup1.select_one('#address span[itemprop="addressRegion"]')
        state = "<MISSING>"
        country_code = soup1.select_one("abbr.c-address-country-name").text
        if _state:
            state = _state.text
        street_address = soup1.select_one('#address meta[itemprop="streetAddress"]')[
            "content"
        ]
        _zip = soup1.select_one('#address span[itemprop="postalCode"]')
        zip = "<MISSING>"
        if _zip:
            zip = _zip.text

        phone = myutil._valid(soup1.select_one("a.Phone-link").text)
        latitude = soup1.select_one('span.coordinates meta[itemprop="latitude"]')[
            "content"
        ]
        longitude = soup1.select_one('span.coordinates meta[itemprop="longitude"]')[
            "content"
        ]
        hours_of_operation = ""
        notification = soup1.select_one(".NotificationBanner-text")
        if notification and (
            "temporarily closed" in notification.text
            or "Permanently Closed." in notification.text
        ):
            hours_of_operation = "Closed"
        else:
            hours = []
            _hours = json.loads(soup1.select_one("div.js-hours-table")["data-days"])
            for _ in _hours:
                hours.append(f'{_["day"]}: {", ".join(_["intervals"])} ')

            hours_of_operation = "; ".join(hours) or "<MISSING>"

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


def fetch_uk(data):
    base_url = "https://stores.burton.co.uk/index.html"
    r = session.get(base_url)
    soup = bs(r.text, "lxml")
    links = soup.select("li.Directory-listItem a.Directory-listLink")
    for link in links:
        page_url = urljoin("https://stores.burton.co.uk/", link["href"])
        parse_detail(page_url, data)


def fetch_ca(data):
    base_url = "https://www.burton.co.uk/store-locator?country=Canada"
    locator_domain = "https://www.burton.co.uk/"
    r = session.get(base_url)
    soup = bs(r.text, "lxml")
    scripts = [
        _.contents[0]
        for _ in soup.select("script")
        if _.contents and '"stores":' in _.contents[0]
    ]
    locations = json.loads(
        scripts[0].split('"stores":')[1].strip().split(',"selectedStore":')[0].strip()
    )
    for location in locations:
        page_url = "<MISSING>"
        location_type = location["brandName"]
        location_name = location["name"]
        street_address = location["address"]["line1"] + myutil._valid1(
            location["address"]["line2"]
        )
        city = myutil._valid(location["address"]["city"])
        country_code = location["address"]["country"]
        state = "<MISSING>"
        zip = myutil._valid(location["address"]["postcode"])
        store_number = location["storeId"]
        phone = myutil._valid(location["telephoneNumber"])
        hours = []
        for key, val in location["openingHours"].items():
            hours.append(f"{key}: {val}")
        hours_of_operation = "; ".join(hours)
        latitude = myutil._valid(location["latitude"])
        longitude = myutil._valid(location["longitude"])

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

    fetch_uk(data)

    fetch_ca(data)

    return data


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
