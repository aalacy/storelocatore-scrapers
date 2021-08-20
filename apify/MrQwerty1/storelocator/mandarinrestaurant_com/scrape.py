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
    locator_domain = "https://www.mandarinrestaurant.com/"
    api_url = "https://www.mandarinrestaurant.com/wp-admin/admin-ajax.php?action=store_search&lat=43.65323&lng=-79.38318&max_results=200&search_radius=2000"
    headers = {
        "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36"
    }

    session = SgRequests()
    r = session.get(api_url, headers=headers)
    js = r.json()

    for j in js:
        street_address = (
            f"{j.get('address')} {j.get('address2') or ''}".strip() or "<MISSING>"
        )
        city = j.get("city") or "<MISSING>"
        state = j.get("state") or "<MISSING>"
        postal = j.get("zip") or "<MISSING>"
        country = j.get("country")
        if "Canada" in country:
            country_code = "CA"
        else:
            country_code = "US"

        store_number = "<MISSING>"
        page_url = j.get("url") or "<MISSING>"
        location_name = j.get("store")
        phone = j.get("phone") or "<MISSING>"
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
        location_type = "<MISSING>"

        source = j.get("hours") or "<html></html>"
        tree = html.fromstring(source)
        text = tree.xpath("//text()")
        text = list(
            filter(
                None,
                [
                    t.replace("CLOSED", "TEMPORARILY CLOSED")
                    .replace("TEMPORARILY", "TEMPORARILY CLOSED")
                    .strip()
                    for t in text
                ],
            )
        )
        text = text[text.index("TAKE-OUT") + 1 : text.index("DELIVERY")]
        hours_of_operation = (
            ";".join(text).replace("CLOSED CLOSED", "CLOSED").replace("day;", "day ")
            or "<MISSING>"
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
