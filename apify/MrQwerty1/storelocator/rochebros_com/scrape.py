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
    locator_domain = "https://rochebros.com/"
    page_url = "https://rochebros.com/locations"
    api_url = "https://strapi.rochebros.com/locations"

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()

    for j in js:
        street_address = j.get("address").replace("\n", ", ")
        city = j.get("city") or "<MISSING>"
        state = j.get("state") or "<MISSING>"
        postal = j.get("zip_code") or "<MISSING>"
        country_code = "US"
        store_number = j.get("id") or "<MISSING>"
        location_name = j.get("location_name")
        phone = j.get("main_phone") or "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        location_type = j.get("location_type") or "<MISSING>"
        hours_of_operation = (
            f"Monday-Saturday:{j.get('mon_to_sat_hours')};Sunday:{j.get('sun_hours')}"
        )

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
