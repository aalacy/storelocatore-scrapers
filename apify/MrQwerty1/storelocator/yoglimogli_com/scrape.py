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
    locator_domain = "https://www.yoglimogli.com/"
    page_url = "https://www.yoglimogli.com/find-a-location"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    script = "".join(tree.xpath("//script[contains(text(), 'markers')]/text()"))
    script = script.split('"markers":')[1].split("]")[0] + "]"
    js = json.loads(script)

    for j in js:
        location_name = j.get("title")
        if "(" in location_name:
            location_name = (
                location_name.split("(")[0].strip()
                + " "
                + location_name.split(")")[1].strip()
            )

        source = j.get("text")
        root = html.fromstring(source)
        street_address = (
            " ".join(
                ", ".join(
                    root.xpath("//span[@itemprop='streetAddress']/text()")
                ).split()
            )
            or "<MISSING>"
        )
        city = (
            "".join(root.xpath("//span[@itemprop='addressLocality']/text()")).strip()
            or "<MISSING>"
        )
        state = (
            "".join(root.xpath("//span[@itemprop='addressRegion']/text()")).strip()
            or "<MISSING>"
        )
        postal = (
            "".join(root.xpath("//span[@itemprop='postalCode']/text()")).strip()
            or "<MISSING>"
        )
        country_code = "US"
        store_number = "<MISSING>"
        phone = (
            "".join(root.xpath("//div[@class='field-content']/text()")).strip()
            or "<MISSING>"
        )
        latitude = j.get("latitude") or "<MISSING>"
        longitude = j.get("longitude") or "<MISSING>"
        location_type = "<MISSING>"
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
