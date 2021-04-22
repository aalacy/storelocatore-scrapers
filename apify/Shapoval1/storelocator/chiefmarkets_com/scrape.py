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
    locator_domain = "https://www.chiefmarkets.com"
    api_url = "https://api.freshop.com/1/stores?app_key=chief_markets&has_address=true&is_selectable=true&limit=100&token=936086459c586517fe05a625bf21f3df"
    location_type = "<MISSING>"
    session = SgRequests()
    r = session.get(api_url)
    js = r.json()
    for j in js["items"]:

        street_address = j.get("address_1")
        phone = "".join(j.get("phone_md")).split("Fax")[0].replace("Phone:", "").strip()
        city = j.get("city")
        postal = j.get("postal_code")
        state = j.get("state")
        country_code = "US"
        store_number = "<MISSING>"
        page_url = j.get("url")
        location_name = j.get("name")
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        hours_of_operation = j.get("hours_md")

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
