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
    locator_domain = "https://www.ochsner.org/"
    api_url = "https://www.ochsner.org/locations"

    session = SgRequests()
    r = session.get(api_url)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@class='location']")

    for d in divs:
        location_name = "".join(d.xpath(".//h4[@class='title']/a/text()")).strip()
        page_url = "".join(d.xpath(".//h4[@class='title']/a/@href"))

        street_address = "".join(d.xpath(".//p[@class='address']/text()")).strip()
        csz = "".join(d.xpath(".//p[@class='city']/text()")).strip()
        city = csz.split(",")[0].strip()
        csz = csz.split(",")[1].strip()
        state = csz.split()[0]
        postal = csz.split()[1]
        country_code = "US"
        store_number = "<MISSING>"
        phone = "".join(d.xpath(".//p[@class='phone']/a/text()")) or "<MISSING>"
        latitude, longitude = "<MISSING>", "<MISSING>"
        location_type = (
            ";".join(d.xpath(".//li[@class='type']/text()")).strip() or "<MISSING>"
        )
        hours_of_operation = (
            " ".join("".join(d.xpath(".//div[@class='hours']//text()")).split())
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
