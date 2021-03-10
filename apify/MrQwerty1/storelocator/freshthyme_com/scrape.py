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
    locator_domain = "https://www.freshthyme.com/"
    api_url = "https://discover.freshthyme.com/api/v2/stores"

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()["items"]

    for j in js:
        a = j.get("address")
        street_address = (
            f"{a.get('address1')} {a.get('address2') or ''}".strip() or "<MISSING>"
        )
        city = a.get("city") or "<MISSING>"
        state = a.get("province") or "<MISSING>"
        postal = a.get("postal_code") or "<MISSING>"
        country_code = "US"
        store_number = j.get("ext_id") or "<MISSING>"
        page_url = f"https://www.freshthyme.com/stores/{store_number}"
        location_name = j.get("name") or "<MISSING>"
        phone = j.get("phone_number") or "<MISSING>"
        loc = j.get("location")
        latitude = loc.get("latitude") or "<MISSING>"
        longitude = loc.get("longitude") or "<MISSING>"
        location_type = "<MISSING>"

        _tmp = []
        hours = j.get("store_hours") or []
        for k, v in hours.items():
            start = v.get("start")
            end = v.get("end")
            if start:
                _tmp.append(f"{k.capitalize()}: {start[:-3]} - {end[:-3]}")
            else:
                _tmp.append(f"{k.capitalize()}: Closed")

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
