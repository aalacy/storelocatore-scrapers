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
    locator_domain = "https://www.afw.com/"

    session = SgRequests()
    r = session.get("https://www.afw.com/stores")
    tree = html.fromstring(r.text)
    text = "".join(
        tree.xpath("//script[contains(text(), 'var yextEntities = ')]/text()")
    )
    text = text.split("var yextEntities = ")[1].strip()[:-1]
    js = json.loads(text)["response"]["entities"]

    for j in js:
        if j.get("closed"):
            continue

        location_name = j.get("name")

        a = j.get("address")
        street_address = f"{a.get('line1')}".strip() or "<MISSING>"
        city = a.get("city") or "<MISSING>"
        state = a.get("region") or "<MISSING>"
        postal = a.get("postalCode") or "<MISSING>"
        country_code = a.get("countryCode") or "<MISSING>"
        page_url = f'https://www.afw.com/stores/{state.lower()}/{city.replace(" ", "-").lower()}'
        store_number = "<MISSING>"
        phone = j.get("mainPhone") or "<MISSING>"
        latitude = j.get("yextDisplayCoordinate", {}).get("latitude") or "<MISSING>"
        longitude = j.get("yextDisplayCoordinate", {}).get("longitude") or "<MISSING>"
        location_type = "<MISSING>"

        hours = j.get("hours") or {}
        _tmp = []
        for k, v in hours.items():
            if k == "holidayHours":
                continue

            day = k
            isclosed = v.get("isClosed")
            if not isclosed:
                interval = v.get("openIntervals")[0]
                start = interval.get("start")
                end = interval.get("end")
                line = f"{day.capitalize()}: {start} - {end}"
                _tmp.append(line)
            else:
                _tmp.append("Closed")
                break

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
