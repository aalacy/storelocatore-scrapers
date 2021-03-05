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
    locator_domain = "https://www.unclemaddios.com/"
    api_url = "https://us-east-1-renderer-read.knack.com/v1/scenes/scene_1/views/view_4/records?rows_per_page=1000"

    headers = {
        "X-Knack-Application-Id": "5522d4b2751e345e19a4086b",
        "X-Knack-REST-API-Key": "renderer",
    }

    session = SgRequests()
    r = session.get(api_url, headers=headers)
    js = r.json()["records"]

    for j in js:
        a = j.get("field_12_raw")
        street_address = (
            f"{a.get('street')} {a.get('street2') or ''}".strip() or "<MISSING>"
        )
        city = a.get("city") or "<MISSING>"
        state = a.get("state") or "<MISSING>"
        postal = a.get("zip") or "<MISSING>"
        country_code = "US"
        store_number = "<MISSING>"
        page_url = "<MISSING>"
        location_name = j.get("field_11")
        phone = j.get("field_13_raw") or {}
        phone = phone.get("formatted") or "<MISSING>"
        latitude = a.get("latitude") or "<MISSING>"
        longitude = a.get("longitude") or "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = j.get("field_15") or "<MISSING>"

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
