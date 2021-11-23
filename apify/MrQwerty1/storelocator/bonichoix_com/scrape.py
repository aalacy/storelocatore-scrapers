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
    locator_domain = "https://www.bonichoix.com/"
    api = "https://www.bonichoix.com/en/store-locator/"

    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    r = session.get(api, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@class='store-result ']")

    for d in divs:
        location_name = "".join(d.xpath(".//span[@class='name']/text()")).strip()
        page_url = "".join(d.xpath(".//a[@class='store-title']/@href"))
        street_address = ", ".join(
            d.xpath(".//span[contains(@class, 'location_address_address')]/text()")
        ).strip()
        city = "".join(d.xpath(".//span[@class='city']/text()")).strip()
        state = "".join(d.xpath(".//span[@class='province']/text()")).strip()
        postal = "".join(d.xpath(".//span[@class='postal_code']/text()")).strip()
        country_code = "CA"
        store_number = "<MISSING>"
        phone = (
            "".join(d.xpath(".//a[contains(@href, 'tel:')]/text()")).strip()
            or "<MISSING>"
        )
        latitude = "".join(d.xpath("./@data-lat")) or "<MISSING>"
        longitude = "".join(d.xpath("./@data-lng")) or "<MISSING>"
        location_type = "<MISSING>"

        _tmp = []
        text = "".join(d.xpath("./@data-hours")) or "{}"
        js = json.loads(text)
        for k, v in js.items():
            if v:
                _tmp.append(f"{k}: {v}")

        hours_of_operation = ";".join(_tmp) or "<MISSING>"

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
