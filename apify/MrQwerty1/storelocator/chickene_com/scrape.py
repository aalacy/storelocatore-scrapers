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
    url = "https://chickene.com/"
    api_url = "https://app.mapply.net/front-end/frontend_json.php?action=load_initial_stores&api_key=mapply.e859d8e82b437f770d4dfa10b9751a14"

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()["initial_stores"]

    for j in js:
        locator_domain = url
        text = j.get("5") or "<html></html>"
        tree = html.fromstring(text)
        location_name = (
            "".join(tree.xpath("//span[@class='name']/text()")).strip() or "<MISSING>"
        )
        street_address = (
            "".join(tree.xpath("//span[@class='address']/text()")).strip()
            or "<MISSING>"
        )
        city = (
            "".join(tree.xpath("//span[@class='city']/text()")).strip() or "<MISSING>"
        )
        state = (
            "".join(tree.xpath("//span[@class='prov_state']/text()")).strip()
            or "<MISSING>"
        )
        postal = (
            "".join(tree.xpath("//span[@class='postal_zip']/text()")).strip()
            or "<MISSING>"
        )
        if not postal[0].isdigit():
            postal = "<MISSING>"
        country_code = "US"
        store_number = j.get("store_id") or "<MISSING>"
        page_url = "https://chickene.com/locations/"
        phone = (
            "".join(tree.xpath("//span[@class='phone']/text()")).strip() or "<MISSING>"
        )
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
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
