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
    locator_domain = "https://www.onepeloton.co.uk/"
    api_url = "https://api.onepeloton.co.uk/ecomm/store"

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()["data"]

    for j in js:
        if not j.get("is_visible"):
            continue
        street_address = f"{j.get('display_street_address_1')} {j.get('display_street_address_2') or ''}".strip()
        city = j.get("display_city") or "<MISSING>"
        state = j.get("display_state") or "<MISSING>"
        postal = j.get("display_postal_code") or "<MISSING>"
        country_code = j.get("country") or "<MISSING>"
        if country_code not in {"US", "CA", "GB"}:
            continue
        store_number = "<MISSING>"
        page_url = f'https://www.onepeloton.co.uk/showrooms/{j.get("slug")}'
        location_name = j.get("display_name")
        phone = j.get("shipping_phone_number") or "<MISSING>"
        latitude = j.get("latitude") or "<MISSING>"
        longitude = j.get("longitude") or "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = ";".join(j.get("hours_of_operation") or []) or "<MISSING>"
        if "http" in hours_of_operation:
            hours_of_operation = "<INACCESSIBLE>"
        if hours_of_operation == "<MISSING>" and country_code == "US":
            hours_of_operation = "<INACCESSIBLE>"
        if j.get("is_coming_soon"):
            hours_of_operation = "Coming Soon"

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
