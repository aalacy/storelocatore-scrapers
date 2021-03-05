import csv
import re

from lxml import html
from sgrequests import SgRequests
from sgselenium import SgFirefox


def write_output(data):
    with open("data.csv", mode="w", encoding="utf8", newline="") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

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

        for row in data:
            writer.writerow(row)


def get_nonce():
    with SgFirefox() as driver:
        driver.get("https://biscuitville.com/")
        source = driver.page_source

    tree = html.fromstring(source)
    text = "".join(tree.xpath("//script[contains(text(), 'nonce')]/text()"))

    return "".join(re.findall(r'"nonce":"(.+)"', text))


def fetch_data():
    out = []
    locator_domain = "https://biscuitville.com/"
    api_url = "https://biscuitville.com/wp-admin/admin-ajax.php"

    data = {
        "action": "get_dl_locations",
        "all": "true",
        "radius": "",
        "lat": "",
        "lng": "",
        "current_location": "Y",
        "nonce": get_nonce(),
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0"
    }

    session = SgRequests()
    r = session.post(api_url, data=data, headers=headers)
    js = r.json()["locations"]

    for state in js.values():
        if state:
            for city in state.values():
                for j in city:
                    street_address = (
                        f"{j.get('address')} {j.get('address2') or ''}".strip()
                        or "<MISSING>"
                    )
                    city = j.get("city") or "<MISSING>"
                    state = j.get("state") or "<MISSING>"
                    postal = j.get("zip") or "<MISSING>"
                    country_code = "US"
                    store_number = j.get("id") or "<MISSING>"
                    page_url = j.get("location_url") or "<MISSING>"
                    location_name = j.get("name")
                    phone = j.get("phone") or "<MISSING>"
                    latitude = j.get("lat") or "<MISSING>"
                    longitude = j.get("lng") or "<MISSING>"
                    location_type = j.get("service_type") or "<MISSING>"
                    hours_of_operation = (
                        j.get("details", "").replace("\r\n", ";") or "<MISSING>"
                    )

                    row = [
                        locator_domain,
                        page_url,
                        location_name,
                        street_address,
                        city,
                        state,
                        postal,
                        country_code,
                        store_number,
                        phone,
                        location_type,
                        latitude,
                        longitude,
                        hours_of_operation,
                    ]
                    out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
