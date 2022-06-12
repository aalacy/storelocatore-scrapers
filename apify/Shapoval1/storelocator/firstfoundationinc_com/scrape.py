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

    locator_domain = "https://www.firstfoundationinc.com"
    api_url = "https://www.firstfoundationinc.com/find-location"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    jsblock = "".join(
        tree.xpath('//script[@data-drupal-selector="drupal-settings-json"]/text()')
    )
    js = json.loads(jsblock)
    for j in js["firstfoundation"]["locations"]:
        slug = "".join(j.get("detailsLink"))
        page_url = f"{locator_domain}{slug}"
        phone = j.get("phone") or "<MISSING>"
        street_address = j.get("address")
        state = j.get("state")
        postal = j.get("zip")
        country_code = "USA"
        city = "".join(j.get("city")).strip()
        location_name = j.get("title")
        location_type = "<MISSING>"
        if "Branch" in location_name:
            location_type = "Branch"
        if "Office" in location_name:
            location_type = "Advisor Offices"
        if "First Foundation" in location_name:
            location_type = "Corporate HQ"
        store_number = "<MISSING>"
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        hours_of_operation = (
            "".join(j.get("hours")).replace("(4pm - 5pm by appointment)", "").strip()
        )
        if hours_of_operation == "By appointment only":
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
