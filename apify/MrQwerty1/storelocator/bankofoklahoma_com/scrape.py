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
    locator_domain = "https://bankofoklahoma.com"
    api_url = "https://bok-dashboard.golocalinteractive.com/api/v1/oklahoma/locations/geocode/75022/5000/all"
    headers = {
        "Authorization": "bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczovL2Jvay1kYXNoYm9hcmQuZ29sb2NhbGludGVyYWN0aXZlLmNvbS9hcGkvdjEvb2tsYWhvbWEvYXV0aCIsImlhdCI6MTYyNDMwNjY3NSwiZXhwIjoxNjI0MzEwMjc1LCJuYmYiOjE2MjQzMDY2NzUsImp0aSI6ImtROWFra0FWMGxTcnB3UWgiLCJzdWIiOjQ5LCJwcnYiOiJhNmRjMGRmNGRjMWE3OTNjMThmODc1N2UxMmFkODdjOGMyOWZlZGM3In0.dXUdTvG8mBroWA04HTHCnJWipnAApaVCE0vfhUhLkzg",
    }

    session = SgRequests()
    r = session.get(api_url, headers=headers)
    js = r.json()

    for j in js:
        location_type = j.get("type")
        if location_type == "ATM":
            continue

        street_address = j.get("address") or "<MISSING>"
        city = j.get("city") or "<MISSING>"
        state = j.get("state") or "<MISSING>"
        postal = j.get("zipcode") or "<MISSING>"
        country_code = "US"
        store_number = j.get("id") or "<MISSING>"
        page_url = (
            f"https://locations.bankofoklahoma.com/bank-locations/-/-/-/{store_number}"
        )
        location_name = j.get("name")
        phone = j.get("contact_phone") or "<MISSING>"
        latitude = j.get("latitude") or "<MISSING>"
        longitude = j.get("longitude") or "<MISSING>"

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
        for d in days:
            if j.get("lobby_temp_closed"):
                _tmp.append("Temporarily Closed")
                break

            part = d[:2].lower()
            start = j.get(f"{part}_open")
            end = j.get(f"{part}_close")
            if not start:
                continue
            _tmp.append(f"{d}: {start} - {end}")

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
