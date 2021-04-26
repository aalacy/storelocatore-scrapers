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


def get_hours(page_url):
    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    line = tree.xpath("//div[@id='storeInfo']/text()")
    line = list(filter(None, [l.strip() for l in line]))
    line = line[line.index("Store Hours:") + 1 :]

    hoo = ";".join(line) or "<MISSING>"
    if "Phone" in hoo:
        hoo = hoo.split(";Phone")[0].strip()

    return hoo


def fetch_data():
    out = []
    locator_domain = "http://foodaramatexas.com/"
    api_url = "http://foodaramatexas.com/locations/_ajax_map.php"

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()

    for j in js:
        location_name = j.get("name")

        street_address = (
            f"{j.get('address1')} {j.get('address2') or ''}".strip() or "<MISSING>"
        )
        city = j.get("city") or "<MISSING>"
        state = j.get("state") or "<MISSING>"
        postal = j.get("zip") or "<MISSING>"
        country_code = "US"
        store_number = j.get("ID") or "<MISSING>"
        page_url = f"http://foodaramatexas.com/locations/{store_number}"
        phone = j.get("phone") or "<MISSING>"
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lon") or "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = get_hours(page_url)

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
