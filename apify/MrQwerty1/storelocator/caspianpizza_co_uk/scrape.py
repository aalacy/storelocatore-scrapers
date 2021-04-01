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


def clean_hours(text):
    text = text.replace(".", ":")
    amount = text.count(":")
    while amount != 1:
        text = text.rsplit(":", 1)[0]
        amount = text.count(":")

    return text


def fetch_data():
    out = []
    locator_domain = "https://caspianpizza.co.uk/"
    page_url = "https://caspianpizza.co.uk/contact.html"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[contains(text(), 'schema.org')]/text()"))
    js = json.loads(text)

    for j in js:
        a = j.get("address")
        street_address = a.get("streetAddress") or "<MISSING>"
        city = a.get("postalCode") or "<MISSING>"
        state = "<MISSING>"
        postal = a.get("addressLocality").strip() or "<MISSING>"
        if " " not in postal:
            state = postal
            postal = "<MISSING>"
        if "," in postal:
            state = postal.split(",")[0].strip()
            postal = postal.split(",")[-1].strip()
        country_code = a.get("addressCountry") or "<MISSING>"
        store_number = "<MISSING>"
        location_name = j.get("name")
        phone = j.get("telephone") or "<MISSING>"
        loc = j.get("geo")
        latitude = loc.get("latitude") or "<MISSING>"
        longitude = loc.get("longitude") or "<MISSING>"
        location_type = "<MISSING>"

        _tmp = []
        hours = j.get("openingHoursSpecification") or []
        for h in hours:
            day = h.get("dayOfWeek").split("/")[-1]
            start = clean_hours(h.get("opens"))
            end = clean_hours(h.get("closes"))
            _tmp.append(f"{day}: {start} - {end}")

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
