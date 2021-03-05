import csv
import json

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
    url = "https://baptist-health.com/"

    session = SgRequests()
    params = (
        ("x-algolia-application-id", "6EH1IB012D"),
        ("x-algolia-api-key", "66eafc59867885378e0a81317ea35987"),
    )
    data = {
        "requests": [
            {
                "indexName": "wp_posts_location",
                "params": "query=&hitsPerPage=5000&maxValuesPerFacet=5000",
            }
        ]
    }
    r = session.post(
        "https://6eh1ib012d-dsn.algolia.net/1/indexes/*/queries",
        params=params,
        data=json.dumps(data),
    )
    js = r.json()["results"][0]["hits"]

    for j in js:
        locator_domain = url
        street_address = (
            f"{j.get('address_1')} {j.get('address_2') or ''}".strip() or "<MISSING>"
        )
        city = j.get("city") or "<MISSING>"
        state = j.get("state") or "<MISSING>"
        postal = j.get("zip_code") or "<MISSING>"
        country_code = "US"
        store_number = j.get("post_id") or "<MISSING>"
        page_url = j.get("permalink") or "<MISSING>"
        location_name = j.get("post_title") or "<MISSING>"
        phone = j.get("phone_number") or "<MISSING>"
        if len(phone) < 10:
            phone = "<MISSING>"
        loc = j.get("_geoloc")
        latitude = loc.get("lat") or "<MISSING>"
        longitude = loc.get("lng") or "<MISSING>"
        location_type = j.get("facility_type") or "<MISSING>"
        hours_of_operation = j.get("operating_hours") or "<MISSING>"

        if hours_of_operation.find("<br/>"):
            hours_of_operation = hours_of_operation.split("<br/>")[0].strip()

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
