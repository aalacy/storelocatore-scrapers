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
    locator_domain = "https://www.countrysidecoop.com/"
    api_url = (
        "https://www.countrysidecoop.com/atlasapi/RPLocationsApi/GetLocations?services="
    )

    session = SgRequests()
    r = session.get(api_url)
    js = json.loads(r.json())

    for j in js:
        street_address = j.get("StreetAddress") or "<MISSING>"
        city = j.get("City") or "<MISSING>"
        state = j.get("State") or "<MISSING>"
        postal = j.get("ZipCode") or "<MISSING>"
        country_code = "US"
        store_number = j.get("LocationsID") or "<MISSING>"
        page_url = f'https://www.countrysidecoop.com{j.get("LocationURL")}'
        location_name = j.get("Name")
        phone = j.get("Phone") or "<MISSING>"
        latitude = j.get("Latitude") or "<MISSING>"
        longitude = j.get("Longitude") or "<MISSING>"
        location_type = "<MISSING>"

        _tmp = []
        source = j.get("Hours") or "<html></html>"
        tree = html.fromstring(source)
        text = tree.xpath("//text()")
        text = list(filter(None, [t.strip() for t in text]))

        for t in text:
            if (
                t.lower().find("hours") != -1
                and t.lower().find("deli") == -1
                and t.find("24") == -1
            ):
                continue
            if t.lower().find("deli") != -1 and t.lower().find("store") == -1:
                break
            if t.find(":") != -1 or t.find("24") != -1:
                _tmp.append(t)

        hours_of_operation = ";".join(_tmp) or "<MISSING>"
        if hours_of_operation.count("Monday") >= 2:
            hours_of_operation = "Monday" + hours_of_operation.split("Monday")[1]

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
