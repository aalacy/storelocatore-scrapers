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


def get_token():
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Accept": "*/*",
        "Accept-Language": "uk-UA,uk;q=0.8,en-US;q=0.5,en;q=0.3",
        "X-Requested-With": "XMLHttpRequest",
        "Connection": "keep-alive",
        "Referer": "https://locations.bankofoklahoma.com/bank-locations",
    }

    r = session.get("https://locations.bankofoklahoma.com/token", headers=headers)

    return r.json()["token"]


def fetch_data():
    out = []
    locator_domain = "https://bankofoklahoma.com"
    api_url = "https://bok-dashboard.golocalinteractive.com/api/v1/oklahoma/locations/geocode/75022/5000/all"
    headers = {
        "Authorization": f"bearer {get_token()}",
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
                _tmp.append(f"{d}: Closed")
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
