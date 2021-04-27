import csv
import re

from lxml import html
from sgrequests import SgRequests
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


def get_coords_from_google_url(url):
    try:
        if url.find("ll=") != -1:
            latitude = url.split("ll=")[1].split(",")[0]
            longitude = url.split("ll=")[1].split(",")[1].split("&")[0]
        else:
            latitude = url.split("@")[1].split(",")[0]
            longitude = url.split("@")[1].split(",")[1]
    except IndexError:
        latitude, longitude = "<MISSING>", "<MISSING>"

    return latitude, longitude


def fetch_data():
    out = []
    locator_domain = "https://www.qualityfoods.com/"
    page_url = "https://www.qualityfoods.com/about-qf/location-hours"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@class='sfContentBlock' and .//a[text()='Map']]")

    for d in divs:
        location_name = " ".join("".join(d.xpath("./h1//text()|./h2//text()")).split())
        line = d.xpath("./div/span/text()")
        line = list(
            filter(None, [l.replace("/", "").replace("\xa0", "").strip() for l in line])
        )[0]
        if " - " in line:
            line = line.split(" - ")[-1]

        adr = parse_address(International_Parser(), line)
        street_address = (
            f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
                "None", ""
            ).strip()
            or "<MISSING>"
        )

        city = adr.city or "<MISSING>"
        state = adr.state or "<MISSING>"
        postal = "<MISSING>"
        country_code = "CA"
        store_number = "<MISSING>"
        phone_text = "".join(d.xpath(".//strong//text()"))
        try:
            phone = re.findall(r"\d{3}-\d{3}-\d{4}", phone_text)[0]
        except IndexError:
            phone = "<MISSING>"

        text = "".join(d.xpath(".//a/@href"))
        if text:
            latitude, longitude = get_coords_from_google_url(text)
        else:
            latitude, longitude = "<MISSING>", "<MISSING>"

        location_type = "<MISSING>"
        hours_of_operation = d.xpath(
            ".//div[./strong/span[contains(text(), 'Store Hours')]]/span//text()|.//strong[contains(text(), 'Store Hours')]/following-sibling::span//text()|.//strong[contains(text(), 'Store Hours')]/following-sibling::text()"
        )
        hours_of_operation = list(filter(None, [h.strip() for h in hours_of_operation]))
        hours_of_operation = "".join(hours_of_operation) or "<MISSING>"
        if "A Step" in hours_of_operation:
            hours_of_operation = hours_of_operation.split("A Step")[0].strip()
        if hours_of_operation.endswith("8"):
            hours_of_operation = hours_of_operation[:-1]

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
