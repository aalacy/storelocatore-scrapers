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
    locator_domain = "https://www.mkbattery.com/"
    api_url = "https://www.mkbattery.com/block/ajax/map/ajax_get_distribution_centers"

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()

    for j in js:
        location_name = j.get("name")

        street_address = (
            f"{j.get('address')} {j.get('address_2') or ''}".strip() or "<MISSING>"
        )
        city = j.get("city") or "<MISSING>"
        state = j.get("state_province") or "<MISSING>"
        postal = j.get("postal_code") or "<MISSING>"
        country_code = j.get("country") or "<MISSING>"
        if country_code == "England":
            country_code = "GB"
        elif country_code == "USA" or country_code == "<MISSING>":
            country_code = "US"
        else:
            continue
        store_number = j.get("id") or "<MISSING>"
        if country_code == "US":
            page_url = "https://www.mkbattery.com/locations/us-distribution-centers"
        else:
            page_url = "https://www.mkbattery.com/locations/uk-distribution-centers"
        phone = j.get("phone") or "<MISSING>"
        latitude = j.get("latitude") or "<MISSING>"
        longitude = j.get("longitude") or "<MISSING>"
        location_type = "<MISSING>"
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
