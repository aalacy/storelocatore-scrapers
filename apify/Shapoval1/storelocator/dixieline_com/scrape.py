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


def get_data():
    rows = []
    locator_domain = "https://www.dixieline.com"
    page_url = "https://www.dixieline.com/Locations"
    session = SgRequests()

    r = session.get(page_url)
    tree = html.fromstring(r.text)
    div = "".join(
        tree.xpath(
            '//div[@id="map_canvas"]/following-sibling::div[1][@id="hiddenLocationData"]/text()'
        )
    )
    js = json.loads(div)
    for j in js:
        street_address = j.get("street")
        city = j.get("city")
        state = j.get("state")
        postal = j.get("zip")
        country_code = "US"
        store_number = "<MISSING>"
        location_name = j.get("branchName")
        phone = j.get("phone")
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        location_type = "<MISSING>"
        hours = j.get("workHour")
        hours = html.fromstring(hours)
        hours_of_operation = " ".join(hours.xpath("//p[1]//text()"))

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

        rows.append(row)
    return rows


def scrape():
    data = get_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
