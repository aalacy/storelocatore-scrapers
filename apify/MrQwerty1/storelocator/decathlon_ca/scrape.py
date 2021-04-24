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
    locator_domain = "https://www.decathlon.ca/"
    api_url = "https://www.decathlon.ca/en/contact-us"

    session = SgRequests()
    r = session.get(api_url)
    tree = html.fromstring(r.text)
    text = "".join(
        tree.xpath("//script[contains(text(), 'var store_marker = []')]/text()")
    ).split("store_marker.push(")[1:]
    for t in text:
        j = json.loads(t.split(");")[0])
        a = j.get("address").split(",")
        postal = a[-1].strip()
        city = a[-2].strip()
        street_address = ", ".join(a[:-2]).strip()
        state = "<MISSING>"
        country_code = "CA"
        store_number = j.get("store_number") or "<MISSING>"
        page_url = j.get("link")
        location_name = j.get("title")
        phone = j.get("phone") or "<MISSING>"
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
        location_type = "<MISSING>"

        _tmp = []
        days = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]
        hours = (
            j.get("hours")
            .replace("&quot;", "")
            .replace("[[", "")
            .replace("]]", "")
            .split("],[")
            or []
        )
        for d, h in zip(days, hours):
            _tmp.append(f"{d}: {h}")

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
