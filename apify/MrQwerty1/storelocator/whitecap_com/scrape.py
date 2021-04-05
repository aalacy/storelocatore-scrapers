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
    url = "https://www.whitecap.com/"
    api_url = "https://www.whitecap.com/locations"

    session = SgRequests()
    r = session.get(api_url)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//div[@id='branch-search']/@data-init"))
    js = json.loads(text)["Branches"]

    for j in js:
        locator_domain = url
        location_name = j.get("AltName") or "<MISSING>"
        a = j.get("Address")
        street_address = (
            f"{a.get('Line1')} {a.get('Line2') or ''}".strip() or "<MISSING>"
        )
        city = a.get("City") or "<MISSING>"
        state = a.get("StateCode") or "<MISSING>"
        postal = a.get("PostalCode") or "<MISSING>"
        country_code = a.get("CountryCode") or "<MISSING>"
        phone = a.get("Phone") or "<MISSING>"
        store_number = j.get("Code") or "<MISSING>"
        page_url = f'https://www.whitecap.com{j.get("Url")}'
        loc = j.get("Coordinates")
        latitude = loc.get("Latitude") or "<MISSING>"
        longitude = loc.get("Longitude") or "<MISSING>"
        location_type = "<MISSING>"

        _tmp = []
        days = [
            "Sunday",
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
        ]
        hours = j.get("WorkingHours", []) or []
        for h in hours:
            day = days[h.get("Day")]
            time = h.get("Hours")
            _tmp.append(f"{day}: {time}".replace("12:00 AM - 12:00 AM", "Closed"))

        hours_of_operation = ";".join(_tmp) or "<MISSING>"

        if hours_of_operation.count("Closed") == 7:
            continue

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
