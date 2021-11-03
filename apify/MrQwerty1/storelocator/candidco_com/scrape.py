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
    locator_domain = "https://candidco.com/"
    api_url = "https://api.candidco.com/api/v1/studios/"

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()

    for j in js:
        location_type = j.get("studio_type") or ""
        if location_type != "retail":
            continue

        a = j.get("studio_address")
        street_address = (
            f"{a.get('thoroughfare')} {a.get('premise') or ''}".strip() or "<MISSING>"
        )
        city = a.get("locality") or "<MISSING>"
        state = a.get("state_name") or "<MISSING>"
        postal = a.get("postal_code") or "<MISSING>"
        country_code = a.get("country") or "<MISSING>"
        store_number = j.get("id") or "<MISSING>"
        page_url = (
            f'https://candidco.com/studios/{j["studio_region"]["slug"]}/{j.get("slug")}'
        )
        location_name = j.get("name")
        phone = j.get("phone") or "<MISSING>"
        latitude = a.get("latitude") or "<MISSING>"
        longitude = a.get("longitude") or "<MISSING>"
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
        out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
