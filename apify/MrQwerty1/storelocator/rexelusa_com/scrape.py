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
    s = set()
    phones = set()
    locator_domain = "https://www.rexelusa.com/"
    api_url = "https://www.rexelusa.com/usr/store-finder"

    session = SgRequests()
    r = session.get(api_url)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//div[@id='map_canvas']/@data-stores"))
    js = json.loads(text)

    for i in range(10000):
        try:
            j = js[f"store{i}"]
        except KeyError:
            break

        location_name = j.get("displayName") or "<MISSING>"
        street_address = (
            f"{j.get('line1')} {j.get('line2') or ''}".strip() or "<MISSING>"
        )
        city = j.get("town") or "<MISSING>"
        state = location_name.split()[0]
        postal = j.get("postalCode") or "<MISSING>"
        country_code = j.get("country") or "<MISSING>"
        if country_code == "United States":
            country_code = "US"

        store_number = j.get("name") or "<MISSING>"
        page_url = f"https://www.rexelusa.com/usr/-/store/{store_number}"
        phone = j.get("phone") or "<MISSING>"
        latitude = j.get("latitude") or "<MISSING>"
        longitude = j.get("longitude") or "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = j.get("hours") or "<MISSING>"

        if hours_of_operation != "<MISSING>":
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

        check = tuple(row[3:6])
        if check not in s and phone not in phones:
            s.add(check)
            phones.add(phone)
            out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
