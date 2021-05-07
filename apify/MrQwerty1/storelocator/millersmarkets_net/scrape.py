import csv
import time

from lxml import html
from sgselenium import SgFirefox


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
    locator_domain = "https://millersmarkets.net/"
    page_url = "https://millersmarkets.net/contact"

    with SgFirefox() as fox:
        fox.get(page_url)
        time.sleep(10)
        source = fox.page_source

    tree = html.fromstring(source)
    divs = tree.xpath("//div[contains(@class, 'fade tab-pane')]")

    for d in divs:
        location_name = "".join(d.xpath(".//h2/text()")).strip()
        street_address = "".join(
            d.xpath(".//h2/following-sibling::p[1]/text()")
        ).strip()
        line = "".join(d.xpath(".//h2/following-sibling::p[2]/text()")).strip()
        city = line.split(",")[0].strip()
        line = line.split(",")[1].strip()
        state = line.split()[0]
        postal = line.split()[1]
        country_code = "US"
        store_number = "<MISSING>"
        phone = (
            "".join(d.xpath(".//a[contains(@href, 'tel:')]/text()")).strip()
            or "<MISSING>"
        )
        text = "".join(d.xpath(".//iframe/@src"))
        try:
            latitude, longitude = text.split("q=")[1].split("&")[0].split(",")
        except:
            latitude, longitude = "<MISSING>", "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = (
            "".join(
                d.xpath(".//b[contains(text(), 'HOURS')]/following-sibling::text()")
            ).strip()
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
