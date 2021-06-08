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

    locator_domain = "https://bigbearfoodmart.ca"

    api_url = "https://bigbearfoodmart.ca/wp-admin/admin-ajax.php?action=store_search&lat=43.255721&lng=-79.871102&max_results=25&search_radius=50&autoload=1"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.post(api_url, headers=headers)
    js = r.json()
    for j in js:

        street_address = f"{j.get('address')} {j.get('address2')}".strip()
        state = j.get("state")
        postal = j.get("zip")
        city = j.get("city")
        country_code = "CA"
        location_type = "<MISSING>"
        store_number = j.get("id")
        location_name = j.get("store")
        phone = j.get("phone") or "<MISSING>"
        latitude = j.get("lat")
        longitude = j.get("lng")
        page_url = j.get("permalink")
        hours = j.get("hours")
        hours = html.fromstring(hours)
        hours_of_operation = (
            " ".join(hours.xpath("//*/text()")).replace("\n", "").strip()
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
