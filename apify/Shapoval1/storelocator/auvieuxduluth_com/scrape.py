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

    locator_domain = "https://auvieuxduluth.com"
    api_url = "https://auvieuxduluth.com/wp-admin/admin-ajax.php?lang=en&action=store_search&lat=45.50169&lng=-73.56726&max_results=36&search_radius=500"

    session = SgRequests()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.post(api_url, headers=headers)

    js = r.json()

    for j in js:

        page_url = j.get("url")
        street_address = f"{j.get('address')} {j.get('address2')}".strip()
        city = "".join(j.get("city")).replace(",", "").strip()
        state = j.get("state")
        postal = j.get("zip")
        store_number = "<MISSING>"
        location_name = "".join(j.get("store")).replace("&#8211;", "-")
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
        country_code = j.get("country")
        location_type = "<MISSING>"
        phone = j.get("phone")
        hours = j.get("hours")
        hours_of_operation = "Closed"
        if hours is not None:
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
