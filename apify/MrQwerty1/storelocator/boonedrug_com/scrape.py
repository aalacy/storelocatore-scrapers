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
    locator_domain = "https://boonedrug.com/"
    api_url = "https://boonedrug.com/locations"

    session = SgRequests()
    r = session.get(api_url)
    tree = html.fromstring(r.text)
    text = "".join(
        tree.xpath("//script[contains(text(), 'openingHoursSpecification')]/text()")
    )
    js = json.loads(text)["@graph"]

    for j in js:
        _type = j.get("@type")
        if _type != "Pharmacy":
            continue

        location_name = j.get("name").strip()
        a = j.get("address")
        street_address = a.get("streetAddress") or "<MISSING>"
        city = a.get("addressLocality") or "<MISSING>"
        state = a.get("addressRegion") or "<MISSING>"
        postal = a.get("postalCode") or "<MISSING>"
        country_code = "US"
        store_number = "<MISSING>"
        phone = a.get("telephone") or "<MISSING>"
        g = j.get("geo")
        latitude = g.get("latitude") or "<MISSING>"
        longitude = g.get("longitude") or "<MISSING>"
        location_type = j.get("@type") or "<MISSING>"

        _tmp = []
        hours = j.get("openingHoursSpecification") or []
        for h in hours:
            day = h.get("dayOfWeek").split("/")[-1]
            start = h.get("opens")
            end = h.get("closes")
            if start != end:
                _tmp.append(f"{day}: {start} - {end}")
            else:
                _tmp.append(f"{day}: Closed")
        hours_of_operation = ";".join(_tmp) or "<MISSING>"
        page_url = (
            f'https://boonedrug.com/stores/{location_name.replace(" ", "-").lower()}'
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
