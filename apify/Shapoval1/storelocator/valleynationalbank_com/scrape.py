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
    locator_domain = "https://www.valley.com/"
    page_url = "https://locations.valley.com/"
    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    block = tree.xpath(
        '//div[@class="no-results"]/li[@class="map-list-item-wrap is-single"]'
    )
    for i in block:
        url1 = "".join(i.xpath(".//a/@href"))
        session = SgRequests()
        r = session.get(url1)
        tree = html.fromstring(r.text)
        block1 = tree.xpath(
            '//ul[@class="map-list browse"]/li[@class="map-list-item-wrap is-single"]'
        )
        for b in block1:
            url2 = "".join(b.xpath(".//a/@href"))
            session = SgRequests()
            r = session.get(url2)
            tree = html.fromstring(r.text)
            block2 = tree.xpath('//div[@class="map-list-inner"]')
            for k in block2:
                location_type = (
                    "".join(k.xpath('.//h5[@class="h5--alt"]/text()'))
                    .replace("\n", "")
                    .strip()
                )
                if location_type == "ATM":
                    continue
                location_name = "".join(
                    k.xpath('.//div[@class="location-name ft-20 mb-15"]/text()')
                )
                page_url = "".join(
                    k.xpath(
                        ".//following-sibling::div[contains(@class, 'map-list-links mt-15')]//a[contains(text(), 'More Info')]/@href"
                    )
                )
                session = SgRequests()
                r = session.get(page_url)
                tree = html.fromstring(r.text)
                block3 = "".join(
                    tree.xpath('//script[@type="application/ld+json"]/text()')
                )
                js = json.loads(block3)
                for j in js:
                    ad = j.get("address")
                    street_address = ad.get("streetAddress")
                    phone = ad.get("telephone") or "<MISSING>"
                    city = ad.get("addressLocality")
                    state = ad.get("addressRegion")
                    country_code = "US"
                    store_number = "<MISSING>"
                    latitude = j.get("geo").get("latitude")
                    longitude = j.get("geo").get("longitude")
                    hours_of_operation = j.get("openingHours")
                    postal = ad.get("postalCode")

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
