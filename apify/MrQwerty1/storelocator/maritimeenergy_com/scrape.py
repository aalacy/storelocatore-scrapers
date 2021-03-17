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
    locator_domain = "https://www.maritimeenergy.com/"
    api_url = "https://www.maritimeenergy.com/stores"

    session = SgRequests()
    r = session.get(api_url)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@class='address card']")

    for d in divs:
        street_address = "".join(
            d.xpath(".//p[@itemprop='streetAddress']/text()")
        ).strip()
        city = "".join(d.xpath(".//span[@itemprop='addressLocality']/text()")).strip()
        state = "".join(d.xpath(".//span[@itemprop='addressRegion']/text()")).strip()
        postal = "".join(d.xpath(".//span[@itemprop='postalCode']/text()")).strip()
        country_code = "US"
        store_number = "<MISSING>"
        slug = "".join(d.xpath(".//h2/a/@href"))
        page_url = f"https://www.maritimeenergy.com{slug}"
        location_name = "".join(d.xpath(".//h2/a/text()")).strip()
        phone = "".join(d.xpath(".//p[@itemprop='telephone']/a/text()"))
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        location_type = "<MISSING>"

        _tmp = []
        li = d.xpath(".//ul[@class='hours']/li")
        for l in li:
            day = "".join(l.xpath("./strong/text()")).strip()
            time = "".join(l.xpath("./text()")).strip()
            _tmp.append(f"{day} {time}")

        hours_of_operation = ";".join(_tmp) or "<MISSING>"

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
