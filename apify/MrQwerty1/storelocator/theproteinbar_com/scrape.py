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
    locator_domain = "https://www.theproteinbar.com"
    api_url = "https://www.theproteinbar.com/restaurants/"

    session = SgRequests()
    r = session.get(api_url)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[contains(text(), 'locations:')]/text()"))
    text = text.split("locations:")[1].split("apiKey")[0].strip()[:-1]
    js = json.loads(text)

    for j in js:
        street_address = j.get("street") or "<MISSING>"
        city = j.get("city") or "<MISSING>"
        state = j.get("state") or "<MISSING>"
        if len(state) > 2:
            continue
        postal = j.get("postal_code") or "<MISSING>"
        country_code = "US"
        store_number = j.get("id") or "<MISSING>"
        page_url = f'https://www.theproteinbar.com{j.get("url")}'
        location_name = j.get("name")
        phone = j.get("phone_number") or "<MISSING>"
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
        location_type = "<MISSING>"

        _tmp = []
        text = j.get("hours") or "<html></html>"
        root = html.fromstring(text)
        days = root.xpath("//p[.//*[contains(text(), 'Mon')]]/strong/text()")
        times = root.xpath("//p[.//*[contains(text(), 'Mon')]]/text()")
        if not times:
            days = root.xpath("//p[.//*[contains(text(), 'Mon')]]/strong/strong/text()")
            times = root.xpath("//p[.//*[contains(text(), 'Mon')]]/strong/text()")

        days = list(filter(None, [d.replace("\xa0", "").strip() for d in days]))
        for d, t in zip(days, times):
            _tmp.append(f"{d.strip()}: {t.strip()}")

        hours_of_operation = (
            ";".join(_tmp).replace("Sat: Fri", "Sat: Closed;Fri") or "<MISSING>"
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
