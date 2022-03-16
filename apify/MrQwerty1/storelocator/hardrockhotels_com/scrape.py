import csv
import time

from lxml import html
from sgselenium.sgselenium import SgFirefox
from sgscrape.sgpostal import parse_address, International_Parser


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
    locator_domain = "https://www.hardrockhotels.com/"
    api_url = "https://www.hardrockhotels.com/destinations.aspx"

    with SgFirefox() as fox:
        fox.get(api_url)
        time.sleep(5)
        source = fox.page_source

    tree = html.fromstring(source)
    divs = tree.xpath(
        "//div[@id='regionNorthAmericaMoreContainer']/div[contains(@class, 'col-xs-12 col-sm-6 col-md-4')]|//div[@id='regionEuropeMoreContainer']//div[contains(@class, 'col-xs-12 col-sm-6 col-md-4') and .//*[contains(text(), 'ENG')]]"
    )

    for d in divs:
        location_name = "".join(
            d.xpath(".//div[@class='locationName']//text()")
        ).strip()
        page_url = (
            "".join(d.xpath(".//div[@class='locationName']/a/@href")) or "<MISSING>"
        )
        if page_url == "<MISSING>":
            continue
        line = "".join(d.xpath(".//div[@class='locationAddress']//text()")).strip()

        adr = parse_address(International_Parser(), line)
        street_address = (
            f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
                "None", ""
            ).strip()
            or "<MISSING>"
        )
        city = adr.city or "<MISSING>"
        state = adr.state or "<MISSING>"
        if city == "<MISSING>" and state == "<MISSING>":
            continue
        postal = adr.postcode or "<MISSING>"
        if len(postal) == 5:
            country_code = "US"
        elif len(postal) == 7:
            country_code = "CA"
        else:
            country_code = "GB"
        store_number = "<MISSING>"
        phone = "<MISSING>"

        text = "".join(d.xpath(".//div[@class='locationAddress']/a/@href")).strip()
        if "q=" in text and "," in text:
            latitude, longitude = text.split("q=")[1].split(",")
        else:
            latitude, longitude = "<MISSING>", "<MISSING>"
        location_type = (
            "".join(d.xpath(".//div[@class='locationFlag']/text()")).strip()
            or "<MISSING>"
        )

        if d.xpath(
            ".//div[@class='comingSoonText']|.//div[contains(@style, 'coming_soon')]"
        ):
            continue

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
