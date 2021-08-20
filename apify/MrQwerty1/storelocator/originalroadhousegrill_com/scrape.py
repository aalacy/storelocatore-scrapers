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
    locator_domain = "https://originalroadhousegrill.com/"
    api_url = "https://originalroadhousegrill.com/locations.html"

    session = SgRequests()
    r = session.get(api_url)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//td[@style='width: 35%; border: none;']")

    for d in divs:
        street_address = (
            "".join(d.xpath(".//span[@class='street-address']/text()")).strip()
            or "<MISSING>"
        )
        city = (
            "".join(d.xpath(".//span[@class='locality']/text()")).strip() or "<MISSING>"
        )
        if city.endswith(","):
            city = city[:-1]
        state = (
            "".join(d.xpath(".//span[@class='region']/text()")).strip() or "<MISSING>"
        )
        postal = (
            "".join(d.xpath(".//span[@class='postal-code']/text()")).strip()
            or "<MISSING>"
        )
        country_code = "US"
        store_number = "<MISSING>"
        slug = "".join(d.xpath(".//strong/a/@href"))
        page_url = f"{locator_domain}{slug}"
        location_name = "".join(d.xpath(".//strong/a/text()")).strip() or "<MISSING>"
        phone = (
            "".join(d.xpath(".//span[@class='phone']/a/text()")).strip() or "<MISSING>"
        )

        latitude = "<MISSING>"
        longitude = "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = (
            "".join(d.xpath(".//span[@class='hours']/text()"))
            .replace("Open", "")
            .strip()
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
