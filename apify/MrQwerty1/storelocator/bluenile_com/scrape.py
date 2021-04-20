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
    locator_domain = "https://www.bluenile.com/"
    api_url = "https://www.bluenile.com/jewelry-stores"

    session = SgRequests()
    r = session.get(api_url)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@class='store']")

    for d in divs:
        street_address = (
            "".join(d.xpath(".//span[@itemprop='streetAddress']/text()")).strip()
            or "<MISSING>"
        )
        if street_address.endswith(","):
            street_address = street_address[:-1]
        city = (
            "".join(d.xpath(".//span[@itemprop='addressLocality']/text()")).strip()
            or "<MISSING>"
        )
        state = (
            "".join(d.xpath(".//span[@itemprop='addressRegion']/text()")).strip()
            or "<MISSING>"
        )
        postal = (
            "".join(d.xpath(".//span[@itemprop='postalCode']/text()")).strip()
            or "<MISSING>"
        )
        country_code = "US"
        store_number = "<MISSING>"
        page_url = (
            "".join(d.xpath(".//a[@class='store-name']/@href")).strip() or "<MISSING>"
        )
        location_name = (
            "".join(d.xpath(".//meta[@itemprop='name']/@content")).strip()
            or "<MISSING>"
        )
        phone = (
            "".join(d.xpath(".//meta[@itemprop='telephone']/@content")).strip()
            or "<MISSING>"
        )
        latitude = "".join(d.xpath("./@data-lat")) or "<MISSING>"
        longitude = "".join(d.xpath("./@data-lng")) or "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = (
            ";".join(d.xpath(".//meta[@itemprop='openingHours']/@content")).strip()
            or "Coming Soon"
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
