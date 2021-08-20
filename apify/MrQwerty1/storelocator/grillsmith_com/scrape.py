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


def get_additional(page_url):
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    hours = tree.xpath(
        "//h2[contains(text(), 'Hours')]/following-sibling::p[not(./a)]//text()"
    )
    hours = ";".join(list(filter(None, [h.strip() for h in hours]))) or "<MISSING>"
    if "temporarily" in hours.lower():
        hours = "Temporarily Closed"

    lat = "".join(tree.xpath("//div[@data-gmaps-lat]/@data-gmaps-lat")) or "<MISSING>"
    lng = "".join(tree.xpath("//div[@data-gmaps-lng]/@data-gmaps-lng")) or "<MISSING>"

    return lat, lng, hours


def fetch_data():
    out = []
    locator_domain = "https://www.grillsmith.com/"
    api_url = "https://www.grillsmith.com/location/Wesley-Chapel/"

    r = session.get(api_url)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[contains(text(), 'Organization')]/text()"))
    js = json.loads(text)["subOrganization"]

    for j in js:
        a = j.get("address")
        street_address = a.get("streetAddress") or "<MISSING>"
        city = a.get("addressLocality") or "<MISSING>"
        state = a.get("addressRegion") or "<MISSING>"
        postal = a.get("postalCode") or "<MISSING>"
        country_code = "US"
        store_number = "<MISSING>"
        page_url = j.get("url")
        location_name = j.get("name")
        phone = j.get("telephone") or "<MISSING>"
        latitude, longitude, hours_of_operation = get_additional(page_url)
        location_type = j.get("@type") or "<MISSING>"

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
