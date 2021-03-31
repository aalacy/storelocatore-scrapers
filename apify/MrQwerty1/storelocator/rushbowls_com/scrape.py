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
    locator_domain = "https://rushbowls.com/"
    api_url = "https://rushbowls.com/locations"

    session = SgRequests()
    r = session.get(api_url)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[contains(text(),'')]/text()"))
    text = text.split("var locations =")[1].split("];")[0] + "]"
    js = json.loads(text)

    for j in js:
        street_address = (
            f"{j.get('fran_address')} {j.get('fran_address_2') or ''}".strip()
            or "<MISSING>"
        )
        city = j.get("fran_city") or "<MISSING>"
        state = j.get("fran_state") or "<MISSING>"
        if len(state) > 2:
            state = "TX"
        postal = j.get("fran_zip") or "<MISSING>"
        country_code = "US"
        store_number = j.get("id") or "<MISSING>"
        page_url = j.get("fran_web_address") or "<MISSING>"
        location_name = j.get("fran_location_name")
        phone = j.get("fran_phone") or "<MISSING>"
        if "coming" in phone.lower():
            phone = "<MISSING>"
        latitude = j.get("fran_latitude") or "<MISSING>"
        longitude = j.get("fran_longitude") or "<MISSING>"
        location_type = "<MISSING>"

        _tmp = []
        source = j.get("fran_hours") or "<html></html>"
        root = html.fromstring(source)
        hours = root.xpath("//text()")
        for h in hours:
            if not h.strip() or "COVID" in h or "2021" in h:
                continue
            if "*" in h or "Under" in h or "Hours" in h:
                break
            _tmp.append(h.strip())

        hours_of_operation = ";".join(_tmp) or "<MISSING>"

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
