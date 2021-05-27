import csv
from lxml import html
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

    locator_domain = "https://www.monsterselfstorage.com/"
    api_url = "https://inventory.g5marketingcloud.com/api/v1/locations?client_id=1106&nearby_locations_below=true&page=1&per_page=100&search_radius=500&sort_by=state_then_city"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()
    for j in js["locations"]:

        location_name = j.get("name")
        location_type = "<MISSING>"
        street_address = j.get("street")
        phone = j.get("phone_number")
        state = j.get("state")
        postal = j.get("postal_code")
        country_code = "US"
        city = j.get("city")
        store_number = "<MISSING>"
        page_url = j.get("home_page_url")
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//span[text()="Office Hours"]/following-sibling::div//text()'
                )
            )
            .replace("\n", "")
            .replace("  ", " ")
            .strip()
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
