import csv
import json
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
    locator_domain = "https://stansdonuts.com"
    api_url = "https://stansdonuts.com/locations/"
    session = SgRequests()
    r = session.get(api_url)
    block = r.text.split('"@graph": ')[1].split("}</script>")[0]
    js = json.loads(block)
    for j in js:
        a = j.get("address")
        location_name = j.get("name")
        street_address = a.get("streetAddress")
        phone = a.get("telephone")
        city = a.get("addressLocality")
        state = a.get("addressRegion")
        country_code = "US"
        store_number = "<MISSING>"
        latitude = j.get("geo").get("latitude")
        longitude = j.get("geo").get("longitude")
        location_type = j.get("@type")
        hours_of_operation = "".join(j.get("openingHours"))
        page_url = "https://stansdonuts.com/locations/"
        postal = a.get("postalCode")
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
