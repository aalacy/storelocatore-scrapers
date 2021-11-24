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
    locator_domain = "https://www.lineagelogistics.com/"
    api = "https://www.lineagelogistics.com/facilities"

    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    r = session.get(api, headers=headers)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[@data-drupal-selector]/text()"))
    js = json.loads(text)["geofield_google_map"][
        "geofield-map-view-facilities-attachment-1"
    ]["data"]["features"]

    for j in js:
        longitude, latitude = j["geometry"]["coordinates"]
        j = j.get("properties")

        text = j.get("description")
        d = html.fromstring(text)

        location_name = (
            "Lineage Logistics "
            + "".join(d.xpath("//p[@class='map-card__type']/text()")).strip()
        )
        street_address = (
            "".join(d.xpath("//span[contains(@class, 'address-line')]/text()")).strip()
            or "<MISSING>"
        )
        city = (
            "".join(d.xpath("//span[@class='locality']/text()")).strip() or "<MISSING>"
        )
        state = (
            "".join(d.xpath("//span[@class='administrative-area']/text()")).strip()
            or "<MISSING>"
        )
        postal = (
            "".join(d.xpath("//span[@class='postal-code']/text()")).strip()
            or "<MISSING>"
        )
        country_code = "<MISSING>"
        store_number = j.get("entity_id") or "<MISSING>"
        phone = (
            "".join(d.xpath("//a[@class='map-card__phone']/text()")).strip()
            or "<MISSING>"
        )
        location_type = "".join(d.xpath("//p[@class='map-card__type']/text()")).strip()
        slug = "".join(d.xpath("//a[@class='link__link']/@href"))
        page_url = f"https://www.lineagelogistics.com{slug}"
        hours_of_operation = "<MISSING>"

        if d.xpath("//a[contains(@href, 'active-construction')]"):
            continue

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
