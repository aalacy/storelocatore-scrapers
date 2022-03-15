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
    locator_domain = "https://www.rexel.co.uk/"
    api_url = "https://www.rexel.co.uk/uki/store-finder"

    session = SgRequests()
    r = session.get(api_url)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//div[@data-stores]/@data-stores"))
    js = json.loads(text).values()

    for j in js:
        street_address = (
            f"{j.get('line1')} {j.get('line2') or ''}".strip() or "<MISSING>"
        )
        city = j.get("town") or "<MISSING>"
        state = "<MISSING>"
        postal = j.get("postalCode") or "<MISSING>"
        country_code = "GB"
        store_number = j.get("name") or "<MISSING>"
        page_url = f"https://www.rexel.co.uk/uki/{city}/store/{store_number}"
        location_name = j.get("displayName")
        phone = j.get("phone") or "<MISSING>"
        latitude = j.get("latitude") or "<MISSING>"
        longitude = j.get("longitude") or "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = j.get("hours") or "<MISSING>"
        hours_of_operation = (
            hours_of_operation.replace("true", "Closed")
            .replace(",", ";")
            .replace("[", "")
            .replace("]", "")
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
