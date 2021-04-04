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
    locator_domain = "https://www.mazzios.com/"
    api_url = "https://www.mazzios.com/find-a-mazzios/"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0"
    }

    session = SgRequests()
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    text = (
        "".join(tree.xpath("//script[contains(text(), 'var gmwMapObjects = ')]/text()"))
        .split("var gmwMapObjects = ")[1]
        .split(";\n")[0]
    )
    js = json.loads(text).get("3").get("locations")

    for j in js:
        root = html.fromstring(j.get("info_window_content"))
        location_name = "".join(root.xpath("//a[@class='title']/text()")) or "<MISSING>"
        street_address = location_name.split(",")[0].strip() or "<MISSING>"
        city = location_name.split(",")[-2].strip() or "<MISSING>"
        state = location_name.split(",")[-1].strip() or "<MISSING>"
        postal = "<MISSING>"
        country_code = "US"
        store_number = "<MISSING>"
        page_url = "".join(root.xpath("//a[@class='title']/@href")) or "<MISSING>"
        phone = "<MISSING>"
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
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
