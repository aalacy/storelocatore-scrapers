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


def fetch_data():
    out = []

    locator_domain = "https://customcomfortmattress.com"
    api_url = "https://code.metalocator.com/index.php?option=com_locator&view=directory&layout=combined_bootstrap&Itemid=14258&tmpl=component&framed=1&source=js"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    jsblock = (
        "".join(tree.xpath('//script[contains(text(), "var location_data")]/text()'))
        .split("var location_data =")[1]
        .split("[]}];")[0]
        .strip()
        + "[]}]"
    )
    js = json.loads(jsblock)

    for j in js:

        page_url = j.get("staticlink")
        location_name = j.get("name")
        location_type = "Custom Comfort Mattress"
        street_address = f"{j.get('address')} {j.get('address2') or ''}".strip()
        phone = j.get("phone")
        state = j.get("state")
        postal = j.get("postalcode")
        country_code = "US"
        city = j.get("city")
        store_number = j.get("id")
        latitude = j.get("lat")
        longitude = j.get("lng")
        hours_of_operation = (
            "".join(j.get("hours"))
            .replace("{", "")
            .replace("}", " ")
            .replace("|", " ")
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
