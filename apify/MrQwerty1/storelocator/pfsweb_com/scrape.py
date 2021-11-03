import csv

import country_converter as coco
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
    locator_domain = "https://www.pfsweb.com/"
    page_url = "https://www.pfsweb.com/contact/"
    cc = coco.CountryConverter()

    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath(
        "//div[contains(@class, 'wpb_column wpb_animate_when_almost_visible') and .//div[@itemprop='address']]"
    )

    for d in divs:
        location_name = "".join(d.xpath(".//span[not(@itemprop)]/text()")).strip()
        street_address = (
            " ".join(
                "".join(d.xpath(".//span[@itemprop='streetAddress']/text()")).split()
            )
            or "<MISSING>"
        )
        city = (
            " ".join(
                "".join(d.xpath(".//span[@itemprop='addressLocality']/text()")).split()
            )
            or "<MISSING>"
        )
        if street_address == "Wide Lane":
            street_address, city = city, street_address
        if street_address.endswith(","):
            street_address = street_address[:-1]
        state = (
            "".join(d.xpath(".//span[@itemprop='addressRegion']/text()")).strip()
            or "<MISSING>"
        )
        postal = (
            "".join(d.xpath(".//span[@itemprop='postalCode']/text()")).strip()
            or "<MISSING>"
        )
        country = "".join(d.xpath(".//span[@itemprop='addressCountry']/text()")).strip()
        country_code = cc.convert(names=[country], to="ISO2")
        store_number = "<MISSING>"
        try:
            phone = d.xpath(".//span[@itemprop='telephone']/text()")[0].strip()
        except IndexError:
            phone = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
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
