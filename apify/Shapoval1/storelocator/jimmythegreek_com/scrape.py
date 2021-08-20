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
    locator_domain = "https://www.jimmythegreek.com"
    api_url = "https://www.jimmythegreek.com/wp-content/themes/jtg/data/locations.json"
    session = SgRequests()

    r = session.get(api_url)
    js = r.json()

    for j in js:
        location_name = j.get("name")
        page_url = "https://www.jimmythegreek.com/locations/"
        street_address = f"{j.get('address')} {j.get('address2')}".strip()
        city = j.get("city")
        state = j.get("state")
        postal = j.get("postal")
        country_code = "CA"
        store_number = "<MISSING>"
        latitude = j.get("lat")
        longitude = j.get("lng")
        location_type = "<MISSING>"
        hours_of_operation = (
            f"{j.get('hours1')} {j.get('hours2')} {j.get('hours3')}".strip()
            or "<MISSING>"
        )
        phone = j.get("phone")

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
