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
    locator_domain = "https://heavenlymassage.com"
    api_url = "https://heavenlymassage.com/wp-admin/admin-ajax.php?action=store_search&lat=41.87811&lng=-87.6298&max_results=25&search_radius=50&autoload=1"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()

    for j in js:
        page_url = "https://heavenlymassage.com/locations/"
        street_address = f"{j.get('address')} {j.get('address2')}".strip()
        city = j.get("city")
        postal = j.get("zip")
        state = j.get("state")
        country_code = j.get("country")
        store_number = "<MISSING>"
        location_name = j.get("store")
        phone = j.get("phone")
        latitude = j.get("lat")
        longitude = j.get("lng")
        location_type = "<MISSING>"
        hours_of_operation = "<MISSING>"
        hours = j.get("hours") or "<MISSING>"
        if hours != "<MISSING>":
            hours = html.fromstring(hours)
            hours_of_operation = (
                " ".join(hours.xpath("//*//text()")).replace("\n", "").strip()
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
