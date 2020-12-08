import csv
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
    url = "https://www.affordabledentures.com/"
    api_url = "https://www.affordabledentures.com/locations.json"

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()["serviceAreas"]["serviceArea"]

    for j in js:
        locator_domain = url
        street_address = j.get("_address") or "<MISSING>"
        city = j.get("_city") or "<MISSING>"
        state = j.get("_state") or "<MISSING>"
        postal = j.get("_zip") or "<MISSING>"
        country_code = "US"
        store_number = j.get("_externalId") or "<MISSING>"
        page_url = f'https://www.affordabledentures.com{j.get("_url")}'
        location_name = j.get("_name") or "<MISSING>"
        phone = j.get("_phone") or "<MISSING>"
        latitude = j.get("_lat") or "<MISSING>"
        longitude = j.get("_lng") or "<MISSING>"
        location_type = "<MISSING>"

        _tmp = []
        hours = j.get("_hours", {}) or {}
        for k, v in hours.items():
            _tmp.append(f"{k.capitalize()}: {v}")

        hours_of_operation = ";".join(_tmp) or "<MISSING>"
        if hours_of_operation.count("Closed") == 7:
            continue

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
