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
    url = "https://www.sinclairoil.com/"
    api_url = "https://www.sinclairoil.com/station-rest-export?_format=json"

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()

    for j in js:
        locator_domain = url
        location_name = "Sinclair"
        street_address = (
            f"{j.get('field_address')} {j.get('field_address_line_2') or ''}".strip()
            or "<MISSING>"
        )
        city = j.get("field_city") or "<MISSING>"
        state = j.get("field_state") or "<MISSING>"
        postal = j.get("field_zipcode") or "<MISSING>"
        if len(postal) == 4:
            postal = f"0{postal}"
        country_code = "US"
        store_number = j.get("title").split(">")[1].split("<")[0]
        page_url = f'https://www.sinclairoil.com{j.get("view_node")}'
        phone = j.get("field_phone_number").replace("+", "-") or "<MISSING>"
        latitude = j.get("field_latitude") or "<MISSING>"
        longitude = j.get("field_longitude") or "<MISSING>"
        if longitude.find(".") == -1:
            longitude = f"{longitude[:4]}.{longitude[4:]}"
        location_type = j.get("field_location_sub_type") or "<MISSING>"
        if location_type.find("(") != -1:
            location_type = location_type.split("(")[0].strip()
        hours_of_operation = "<INACCESSIBLE>"

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
