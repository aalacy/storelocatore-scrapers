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
    locator_domain = "https://www.caesars.com/horseshoe"
    api_url = "https://www.caesars.com/api/v1/properties"

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()

    for j in js:
        brand = j.get("brand")
        if brand != "horseshoe":
            continue

        a = j.get("address")
        street_address = a.get("street") or "<MISSING>"
        city = a.get("city") or "<MISSING>"
        state = a.get("state") or "<MISSING>"
        postal = a.get("zip") or "<MISSING>"
        country_code = "US"
        store_number = "<MISSING>"
        page_url = j.get("url") or "<MISSING>"
        location_name = j.get("name")
        phone = j.get("phone").replace("SHOE/", "") or "<MISSING>"
        loc = j.get("location")
        latitude = loc.get("latitude") or "<MISSING>"
        longitude = loc.get("longitude") or "<MISSING>"
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
