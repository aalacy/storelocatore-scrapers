import csv

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


def fetch_data():
    out = []
    s = set()
    locator_domain = "https://laboiteverte.com/"
    page_url = "https://laboiteverte.com/"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    divs = tree.xpath(
        "//div[@class='elementor-text-editor elementor-clearfix' and ./h1]"
    )[2:]

    for d in divs:
        location_name = "".join(d.xpath("./h1/strong/text()")).strip()
        if location_name in s:
            continue

        s.add(location_name)
        line = "".join(d.xpath("./h1/following-sibling::p[1]/text()")).strip()
        postal = " ".join(line.split()[-2:])
        adr = parse_address(International_Parser(), line, postcode=postal)
        street_address = (
            f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
                "None", ""
            ).strip()
            or "<MISSING>"
        )
        city = adr.city or "<MISSING>"
        state = adr.state or "<MISSING>"
        postal = adr.postcode or "<MISSING>"
        country_code = "CA"

        store_number = "<MISSING>"
        phone = (
            "".join(
                d.xpath("./h1/following-sibling::p[contains(text(), 'Tel')]/text()")
            )
            .replace("Tel", "")
            .replace(":", "")
            .strip()
            or "<MISSING>"
        )
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = (
            "".join(
                d.xpath("./h1/following-sibling::p[contains(text(), 'hours')]/text()")
            )
            .replace("Opening hours:", "")
            .strip()
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
