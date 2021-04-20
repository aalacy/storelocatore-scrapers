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
    coords = dict()
    locator_domain = "https://www.buckmason.com/"
    api_url = "https://www.buckmason.com/pages/our-stores"

    session = SgRequests()
    r = session.get(api_url)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[@id='JSON_locations']/text()"))
    divs = tree.xpath("//figure[@class='stores-menu__item']")

    js = json.loads(text)
    for j in js:
        key = j.get("address_zip").split("-")[0]
        val = j.get("coordinates")
        coords[key] = val

    for d in divs:
        location_name = "".join(
            d.xpath(".//h2[@class='stores-menu__name']/text()")
        ).strip()
        line = d.xpath(".//div[@class='stores-menu__address']/text()")
        line = list(filter(None, [l.strip() for l in line]))

        street_address = ", ".join(line[:-1])
        line = line[-1]
        city = line.split(",")[0].strip()
        line = line.split(",")[1].strip()
        state = line.split()[0]
        postal = line.split()[-1]
        country_code = "US"
        store_number = "<MISSING>"
        slug = "".join(d.xpath("./a[@class='stores-menu__link']/@href"))
        page_url = f"https://www.buckmason.com{slug}"
        phone = (
            "".join(d.xpath(".//a[@class='stores-menu__telephone']/text()"))
            or "<MISSING>"
        )
        latitude, longitude = coords[postal]
        location_type = "<MISSING>"

        hours = d.xpath(".//div[@class='stores-menu__hours']/text()")
        hours = list(filter(None, [h.strip() for h in hours]))[1:]
        hours_of_operation = ";".join(hours) or "<MISSING>"

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
