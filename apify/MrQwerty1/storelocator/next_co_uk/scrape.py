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
    locator_domain = "https://www.next.co.uk/"
    api_url = "https://stores.next.co.uk/stores/country/United%20Kingdom"

    session = SgRequests()
    r = session.get(api_url)
    tree = html.fromstring(r.text)
    text = "".join(
        tree.xpath("//script[contains(text(), 'window.lctr.results.push(')]/text()")
    ).split("\n")

    for t in text:
        if not t.strip().startswith("window.lctr.results.push("):
            continue

        t = t.split("window.lctr.results.push(")[1].split(");")[0]
        j = json.loads(t)
        street_address = (
            f"{j.get('AddressLine')} {j.get('street') or ''}".strip() or "<MISSING>"
        )
        street_address = " ".join(street_address.split())
        city = j.get("city") or "<MISSING>"
        state = j.get("county") or "<MISSING>"
        postal = j.get("PostalCode") or "<MISSING>"
        country_code = "GB"
        store_number = j.get("location_id") or "<MISSING>"
        page_url = f"https://stores.next.co.uk/results/infowindow/{store_number}"
        location_name = j.get("branch_name")
        phone = j.get("telephone") or "<MISSING>"
        latitude = j.get("Latitude") or "<MISSING>"
        longitude = j.get("Longitude") or "<MISSING>"
        location_type = "<MISSING>"

        _tmp = []
        days = ["mon", "tues", "weds", "thurs", "fri", "sat", "sun"]
        for d in days:
            start = j.get(f"{d}_open")
            close = j.get(f"{d}_close")
            if start.strip() != "0" and start.strip() and start.strip() != "Store":
                if len(start) == 3:
                    start = f"0{start}"

                _tmp.append(
                    f"{d.capitalize()}: {start[:2]}:{start[2:]} - {close[:2]}:{close[2:]}"
                )
            else:
                _tmp.append(f"{d.capitalize()}: Closed")

        hours_of_operation = ";".join(_tmp) or "<MISSING>"
        if hours_of_operation.count("Closed") >= 6:
            hours_of_operation = "Closed"

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
