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
    locator_domain = "https://bigredliquors.com/"
    api_url = "https://bigredliquors.com/store-locator/"

    session = SgRequests()
    r = session.get(api_url)
    tree = html.fromstring(r.text)
    text = "".join(
        tree.xpath(
            "//script[contains(text(), 'cityHiveWidgetAPIResourceStorage')]/text()"
        )
    )
    text = text.split('JSON.parse("')[2].split('");')[0].replace("\\", "")
    js = json.loads(text)["merchant_configs"]

    for j in js:
        j = j.get("merchant")
        location_name = j.get("name")
        status = j.get("onboarding_state")
        if status != "active":
            continue
        if location_name.lower().find("big red #") == -1:
            continue
        a = j.get("address")
        street_address = a.get("street_address") or "<MISSING>"
        city = a.get("city") or "<MISSING>"
        state = a.get("state") or "<MISSING>"
        postal = a.get("zipcode") or "<MISSING>"
        country_code = a.get("country_code") or "<MISSING>"
        store_number = location_name.split("#")[1].split()[0]
        page_url = "<MISSING>"
        phone = j.get("phone_number") or "<MISSING>"
        loc = a.get("address_properties") or {}
        latitude = loc.get("lat") or "<MISSING>"
        longitude = loc.get("lng") or "<MISSING>"
        location_type = j.get("type") or "<MISSING>"

        _tmp = []
        hours = j.get("business_hours")
        for k, v in hours.items():
            if v.get("opening"):
                _tmp.append(f'{k}: {v.get("opening")} - {v.get("closing")}')
            else:
                _tmp.append(f"{k}: Closed")

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
