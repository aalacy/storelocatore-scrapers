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
    locator_domain = "https://www.houseoffraser.co.uk/"
    api_url = "https://www.houseoffraser.co.uk/stores/search?countryName=United%20Kingdom&countryCode=GB&lat=0&long=0&sd=500"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0"
    }

    session = SgRequests()
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[contains(text(), 'var stores =')]/text()"))
    text = text.split("var stores =")[1].split("var searchLocationLat")[0].strip()[:-1]
    js = json.loads(text)

    for j in js:
        street_address = j.get("address") or "<MISSING>"
        city = j.get("town") or "<MISSING>"
        state = j.get("county") or "<MISSING>"
        postal = j.get("postCode") or "<MISSING>"
        country_code = j.get("countryCode") or "<MISSING>"
        store_number = j.get("code") or "<MISSING>"
        page_url = f'https://www.houseoffraser.co.uk/{j.get("storeUrl")}'
        location_name = j.get("formattedStoreNameLong")
        phone = j.get("telephone") or "<MISSING>"
        latitude = j.get("latitude") or "<MISSING>"
        longitude = j.get("longitude") or "<MISSING>"
        location_type = j.get("storeType") or "<MISSING>"

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
        hours = j.get("openingTimes") or []

        for h in hours:
            day = days[h.get("dayOfWeek")]
            start = h.get("openingTime")
            close = h.get("closingTime")
            _tmp.append(f"{day}: {start} - {close}")

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
