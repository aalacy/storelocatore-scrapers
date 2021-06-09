import csv
import json

from concurrent import futures
from sgrequests import SgRequests
from sgzip.static import static_coordinate_list, SearchableCountries


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


def get_data(coord):
    rows = []
    lat, lng = coord
    locator_domain = "https://www.capitalone.com/bank/atm/"

    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Accept": "application/json;v=1",
        "Accept-Language": "uk-UA,uk;q=0.8,en-US;q=0.5,en;q=0.3",
        "Content-Type": "application/json",
        "Origin": "https://locations.capitalone.com",
        "Connection": "keep-alive",
        "Referer": "https://locations.capitalone.com/",
    }

    data = {
        "variables": {
            "input": {
                "lat": float(lat),
                "long": float(lng),
                "radius": 25,
                "locTypes": ["atm"],
                "servicesFilter": [],
            }
        },
        "query": "\n        query geoSearch($input: GeoSearchInput!){\n          geoSearch(input: $input){\n            locType\n            locationName\n            locationId\n            address {\n              addressLine1\n              stateCode\n              postalCode\n              city\n            }\n            services\n            distance\n            latitude\n            longitude\n            slug\n            seoType\n            ... on Atm {\n              open24Hours\n            }\n            ... on Branch {\n              phoneNumber\n              timezone\n              lobbyHours {\n                day\n                open\n                close\n              }\n              driveUpHours {\n                day\n                open\n                close\n              }\n              temporaryMessage\n              reopenDate\n            }\n            ... on Cafe {\n              phoneNumber\n              photo\n              timezone\n              hours {\n                day\n                open\n                close\n              }\n              temporaryMessage\n              reopenDate\n            }\n          }\n        }",
    }

    r = session.post(
        "https://api.capitalone.com/locations", headers=headers, data=json.dumps(data)
    )
    js = r.json()["data"]["geoSearch"]

    for j in js:
        a = j.get("address")
        street_address = (
            f"{a.get('addressLine1')} {a.get('addressLine2') or ''}".strip()
            or "<MISSING>"
        )
        city = a.get("city") or "<MISSING>"
        state = a.get("stateCode") or "<MISSING>"
        postal = a.get("postalCode") or "<MISSING>"
        country_code = "US"
        store_number = j.get("locationId") or "<MISSING>"
        page_url = f'https://locations.capitalone.com/-/-/{j.get("slug")}'
        location_name = j.get("locationName")
        phone = "<MISSING>"
        latitude = j.get("latitude") or "<MISSING>"
        longitude = j.get("longitude") or "<MISSING>"
        location_type = j.get("locType") or "<MISSING>"
        hours_of_operation = "<MISSING>"

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
        rows.append(row)

    return rows


def fetch_data():
    out = []
    s = set()
    coords = static_coordinate_list(radius=25, country_code=SearchableCountries.USA)

    with futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_url = {executor.submit(get_data, coord): coord for coord in coords}
        for future in futures.as_completed(future_to_url):
            rows = future.result()
            for row in rows:
                _id = row[8]
                if _id not in s:
                    s.add(_id)
                    out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
