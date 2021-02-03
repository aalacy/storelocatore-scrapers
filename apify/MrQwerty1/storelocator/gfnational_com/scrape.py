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
    locator_domain = "https://gfnational.com/"
    page_url = "https://gfnational.com/Locations"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[contains(text(), '\"markers\":')]/text()"))
    text = text.split('"markers":')[1].split("}));")[0]
    js = json.loads(text)

    for j in js:
        t = html.fromstring(j.get("listHtml"))
        street_address = (
            "".join(t.xpath(".//span[@class='loc-street']/text()")).strip()
            or "<MISSING>"
        )
        city = (
            "".join(t.xpath(".//span[@class='loc-city']/text()")).strip() or "<MISSING>"
        )
        state = (
            "".join(t.xpath(".//span[@class='loc-state']/text()")).strip()
            or "<MISSING>"
        )
        postal = (
            "".join(t.xpath(".//span[@class='loc-zip']/text()")).strip() or "<MISSING>"
        )
        country_code = "US"
        store_number = "<MISSING>"
        location_name = "".join(t.xpath("./p/strong/text()")).strip() or "<MISSING>"
        phone = (
            "".join(t.xpath(".//span[@class='loc-phone']/text()")).strip()
            or "<MISSING>"
        )
        loc = j.get("position") or {}
        latitude = loc.get("latitude") or "<MISSING>"
        longitude = loc.get("longitude") or "<MISSING>"
        location_type = "<MISSING>"

        hours_of_operation = (
            ";".join(t.xpath(".//div[@class='loc-lobby-hours']//li/text()"))
            or "<MISSING>"
        )
        if hours_of_operation.find("All") != -1:
            hours_of_operation = "<MISSING>"

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
