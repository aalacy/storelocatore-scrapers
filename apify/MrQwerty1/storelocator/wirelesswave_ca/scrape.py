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
    locator_domain = "https://www.wirelesswave.ca/"
    api_url = "https://www.wirelesswave.ca/en/locations/"

    session = SgRequests()
    r = session.get(api_url)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[contains(text(),'page.locations =')]/text()"))
    text = text.split("page.locations =")[1].split(";")[0].strip()
    js = json.loads(text)

    for j in js:
        street_address = (
            f"{j.get('Address')} {j.get('Address2') or ''}".strip() or "<MISSING>"
        )
        city = j.get("CountryCode") or "<MISSING>"
        state = j.get("ProvinceAbbrev") or "<MISSING>"
        postal = j.get("PostalCode") or "<MISSING>"
        country_code = j.get("CountryCode") or "<MISSING>"
        store_number = j.get("LocationId") or "<MISSING>"
        page_url = f"https://www.wirelesswave.ca/en/locations/{store_number}/"
        location_name = " ".join(j.get("Name").replace("WW ", "").split()[:-2])
        phone = j.get("Phone") or "<MISSING>"
        latitude = j.get("Google_Latitude") or "<MISSING>"
        longitude = j.get("Google_Longitude") or "<MISSING>"
        location_type = "<MISSING>"

        _tmp = []
        hours = j.get("HoursOfOperation") or []
        for h in hours:
            day = h.get("DayOfWeek")
            start = h.get("Open")
            end = h.get("Close")
            if start and end:
                start, end = str(start), str(end)
                if len(start) == 3:
                    start = f"0{start}"

                _tmp.append(f"{day}: {start[:2]}:{start[2:]} - {end[:2]}:{end[2:]}")
            else:
                _tmp.append(f"{day}: Closed")

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
