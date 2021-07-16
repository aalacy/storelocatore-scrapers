import csv
import json

from sgrequests import SgRequests
from lxml import html


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
    locator_domain = "https://www.deaconess.com/"

    session = SgRequests()
    params = (
        ("x-algolia-application-id", "384Z147YW1"),
        ("x-algolia-api-key", "eb5ea2fbb3f31a5f31b8236aaad3d350"),
    )
    data = {
        "requests": [
            {
                "indexName": "PRD_Locations",
                "params": "query=&hitsPerPage=5000&maxValuesPerFacet=5000",
            }
        ]
    }
    r = session.post(
        "https://384z147yw1-2.algolianet.com/1/indexes/*/queries",
        params=params,
        data=json.dumps(data),
    )
    js = r.json()["results"][0]["hits"]

    for j in js:
        street_address = j.get("StreetAddress") or "<MISSING>"
        city = j.get("City") or "<MISSING>"
        state = j.get("State") or "<MISSING>"
        postal = j.get("Zip") or "<MISSING>"
        country_code = "US"
        store_number = j.get("ItemID") or "<MISSING>"
        page_url = j.get("permalink") or "<MISSING>"
        location_name = j.get("LocationName") or "<MISSING>"
        phone = j.get("Phone").replace("&nbsp;", "").strip() or "<MISSING>"
        if ">" in phone:
            phone = phone.split(">")[1].split("<")[0]
        if "(" in phone:
            phone = phone.split("(")[0].strip()
        if "E" in phone:
            phone = phone.split("E")[0].strip()
        loc = j.get("_geoloc")
        latitude = loc.get("lat") or "<MISSING>"
        longitude = loc.get("lon") or "<MISSING>"
        location_type = j.get("LocationTypeName") or "<MISSING>"
        if "-" in location_type:
            location_type = location_type.split("-")[-1].strip()

        _tmp = []
        source = j.get("OfficeHours") or "<html></html>"
        tree = html.fromstring(source)
        for t in tree.xpath("//text()"):
            if (
                "*" in t
                or "vary" in t.lower()
                or "Located" in t
                or "Patients" in t
                or not t.strip()
            ):
                continue
            _tmp.append(t.replace("&nbsp;", " ").strip())

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
            phone or "<MISSING>",
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
