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
    locator_domain = "https://www.halfords.com/"
    api_url = "https://www.halfords.com/locations"

    session = SgRequests()
    r = session.get(api_url)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[@class='js-stores']/text()"))
    js = json.loads(text)["stores"]

    for j in js:
        street_address = (
            f"{j.get('address1')} {j.get('address2') or ''}".strip() or "<MISSING>"
        )
        city = j.get("city") or "<MISSING>"
        state = j.get("stateCode") or "<MISSING>"
        postal = j.get("postalCode") or "<MISSING>"
        country_code = j.get("countryCode")
        store_number = j.get("ID") or "<MISSING>"
        page_url = j.get("storeDetailsLink") or "<MISSING>"
        location_name = j.get("name")
        phone = j.get("phone") or "<MISSING>"
        latitude = j.get("latitude") or "<MISSING>"
        longitude = j.get("longitude") or "<MISSING>"
        location_type = j.get("storeType") or "<MISSING>"

        _tmp = []
        hours = j.get("storeHours").get("workingHours") or {}
        for h in hours:
            for k, v in h.items():
                start = v[0].get("Start") or ""
                close = v[0].get("Finish") or ""

                if start.strip() != close.strip():
                    _tmp.append(f"{k}: {start.strip()} - {close.strip()}")
                else:
                    _tmp.append(f"{k}: Closed")

        hours_of_operation = ";".join(_tmp) or "<MISSING>"
        if hours_of_operation.count("Closed") == 7:
            hours_of_operation = "Closed"

        try:
            message = j.get("custom").get("emergencyMessage").get("markup") or ""
            if message.lower().find("closed") != -1:
                hours_of_operation = "Closed"
        except:
            pass

        if not location_name:
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
