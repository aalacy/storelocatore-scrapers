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
    locator_domain = "https://stansdonuts.com"
    api_url = "https://stansdonuts.com/wp-admin/admin-ajax.php?action=store_search&lat=41.87811&lng=-87.6298&max_results=25&search_radius=50&autoload=1"
    session = SgRequests()
    r = session.get(api_url)

    js = r.json()
    for j in js:
        location_name = j.get("store")
        street_address = f"{j.get('address')} {j.get('address2')}".strip()
        phone = j.get("phone")
        city = j.get("city")
        state = j.get("state")
        country_code = j.get("country")
        store_number = "<MISSING>"
        latitude = j.get("lat")
        longitude = j.get("lng")
        location_type = "<MISSING>"
        hours = j.get("hours")
        hours = html.fromstring(hours)
        hours_of_operation = (
            " ".join(hours.xpath("//tr//text()")).replace("\n", "").strip()
        )
        page_url = "https://stansdonuts.com/locations/"
        postal = j.get("zip")
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
