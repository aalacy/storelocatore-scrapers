import csv
import json
from lxml import html
from sgrequests import SgRequests


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


def fetch_data():
    out = []
    locator_domain = "https://www.afbasket.com"
    page_url = "https://www.afbasket.com/locations/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }
    r = session.get(page_url, headers=headers)
    block = r.text.split("var stores = ")[1].split(";")[0]
    js = json.loads(block)

    for j in js:

        street_address = j.get("address1")
        city = j.get("city")
        postal = j.get("zipCode")
        state = j.get("state")
        country_code = "US"
        store_number = j.get("storeNumber")
        location_name = j.get("name")
        phone = j.get("phone")
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        location_type = "<MISSING>"
        hours = j.get("hourInfo")
        hours = html.fromstring(hours)
        hours_of_operation = (
            " ".join(hours.xpath("//*//text()"))
            .replace("\n", "")
            .split("4th")[0]
            .strip()
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
