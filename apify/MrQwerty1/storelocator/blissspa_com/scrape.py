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
    locator_domain = "https://www.blissspa.com/"
    page_url = "https://www.blissspa.com/locations/"

    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@class='wpsl-stores']")[0].xpath(".//li")

    for d in divs:
        location_name = "".join(
            d.xpath(".//div[@class='spa-location-description']/strong/text()")
        ).strip()
        line = d.xpath(".//div[@class='spa-location-description']/span/text()")
        line = list(filter(None, [l.strip() for l in line]))
        street_address = ", ".join(line[:-1])
        line = line[-1].replace("DC,", ", DC")
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
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        location_type = "<MISSING>"

        hours = d.xpath(".//p[@class='wpsl-contact-details']/span[last()]/text()")
        if d.xpath(
            ".//p[@class='wpsl-contact-details']/strong[contains(text(), 'New Hours')]"
        ):
            hours = d.xpath(".//p[@class='wpsl-contact-details']/text()")
        hours = list(filter(None, [h.strip() for h in hours]))
        hours_of_operation = ";".join(hours).replace(":", "").strip() or "<MISSING>"

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
