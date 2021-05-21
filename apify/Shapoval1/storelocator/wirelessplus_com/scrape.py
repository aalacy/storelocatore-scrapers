import csv
import json
from datetime import datetime
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
    locator_domain = "https://www.wirelessplus.com"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
    }

    r = session.get("https://www.wirelessplus.com/locations/", headers=headers)
    tree = html.fromstring(r.text)
    jsblock = (
        "".join(tree.xpath('//script[contains(text(), "page.locations")]/text()'))
        .split("page.locations = ")[1]
        .split(";")[0]
        .strip()
    )
    js = json.loads(jsblock)
    for j in js:

        street_address = f"{j.get('Address')} {j.get('Address2') or ''}".replace(
            "None", ""
        ).strip()
        city = "".join(j.get("City")).replace("(DTLA)", "")
        state = j.get("ProvinceAbbrev")
        postal = j.get("PostalCode")
        location_name = j.get("Name")
        country_code = j.get("CountryCode")
        store_number = j.get("LocationId")
        latitude = j.get("Position").get("Latitude")
        longitude = j.get("Position").get("Longitude")
        if latitude == longitude:
            latitude, longitude = "<MISSING>", "<MISSING>"
        location_type = "<MISSING>"
        slug = "".join(city).lower()
        if slug.find(" ") != -1:
            slug = slug.replace(" ", "-")
        if store_number == 134840:
            slug = "dtla-olive"
        if store_number == 159025:
            slug = "dtla-wakaba"
        page_url = f"https://www.wirelessplus.com/locations/{store_number}/{slug}"
        hours = j.get("HoursOfOperation")
        tmp = []
        for h in hours:
            day = h.get("DayOfWeek")

            try:
                opens = datetime.strptime(str(h.get("Open")), "%H%M").strftime(
                    "%I:%M %p"
                )
                closes = datetime.strptime(str(h.get("Close")), "%H%M").strftime(
                    "%I:%M %p"
                )
            except ValueError:
                opens = "Close"
                closes = "Close"
            line = f"{day} {opens} - {closes}"
            if opens == "Close" and closes == "Close":
                line = f"{day} Closed"
            tmp.append(line)
        hours_of_operation = ";".join(tmp) or "<MISSING>"
        phone = j.get("Phone")

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
