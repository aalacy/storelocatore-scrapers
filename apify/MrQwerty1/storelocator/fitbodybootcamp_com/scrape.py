import csv
import json

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


def get_phone(page_url):
    if page_url == "<MISSING>":
        return "<MISSING>"

    r = session.get(page_url)
    tree = html.fromstring(r.text)

    return (
        "".join(tree.xpath("//p[@class='foot-address']/a/text()")).strip()
        or "<MISSING>"
    )


def fetch_data():
    out = []
    locator_domain = "https://fitbodybootcamp.com/"
    api_url = "https://code.metalocator.com/index.php?user_lat=0&user_lng=0&postal_code=75022&Itemid=12087&view=directory&layout=combined&tmpl=component&framed=1&preview=0&parent_table=&parent_id=0&task=search_zip&search_type=point&_opt_out=&option=com_locator&ml_location_override=&limitstart=0&limit=5000"

    r = session.get(api_url)
    tree = html.fromstring(r.text)
    text = "".join(
        tree.xpath("//script[contains(text(), 'var location_data =')]/text()")
    )
    text = text.split("var location_data =")[1].split("];")[0] + "]"
    js = json.loads(text)

    for j in js:
        street_address = j.get("address") or "<MISSING>"
        city = j.get("city") or "<MISSING>"
        state = j.get("state") or "<MISSING>"
        postal = j.get("postalcode") or "<MISSING>"
        country_code = j.get("country") or "US"
        store_number = j.get("id") or "<MISSING>"
        page_url = j.get("link") or "<MISSING>"
        location_name = j.get("name")
        phone = j.get("phone") or get_phone(page_url)
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
    session = SgRequests()
    scrape()
