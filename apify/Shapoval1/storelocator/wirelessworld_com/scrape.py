import csv
from datetime import datetime
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

    locator_domain = "https://www.wirelessworld.com"
    api_url = "https://www.wirelessworld.com/locations/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    jsblock = (
        "".join(tree.xpath('//script[contains(text(), "page.locations")]/text()'))
        .split("page.locations = ")[1]
        .split(";")[0]
        .strip()
    )

    js = json.loads(jsblock)
    for j in js:

        location_name = j.get("Name")
        location_type = "store"
        street_address = f"{j.get('Address')} {j.get('Address2') or ''}".replace(
            "None", ""
        ).strip()
        phone = j.get("Phone")
        state = j.get("ProvinceAbbrev")
        postal = j.get("PostalCode")
        country_code = j.get("CountryCode")
        city = j.get("City")
        slug = "".join(city).lower().replace(" ", "-")
        store_number = j.get("LocationId")
        page_url = f"https://www.wirelessworld.com/locations/{store_number}/{slug}/"
        latitude = j.get("Google_Latitude")
        longitude = j.get("Google_Longitude")
        hours = j.get("HoursOfOperation")
        tmp = []
        for h in hours:
            day = h.get("DayOfWeek")
            try:
                opens = datetime.strptime(str(h.get("Open")), "%H%M").strftime(
                    "%I:%M %p"
                )
                close = datetime.strptime(str(h.get("Close")), "%H%M").strftime(
                    "%I:%M %p"
                )
            except:
                opens = "Closed"
                close = "Closed"
            line = f"{day} {opens} - {close}"
            if opens == "Closed" and close == "Closed":
                line = f"{day} - Closed"
            tmp.append(line)

        hours_of_operation = ";".join(tmp) or "<MISSING>"

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
