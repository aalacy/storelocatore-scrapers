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


def get_coords_from_embed(text):
    try:
        latitude = text.split("!3d")[1].strip().split("!")[0].strip()
        longitude = text.split("!2d")[1].strip().split("!")[0].strip()
    except IndexError:
        latitude, longitude = "<MISSING>", "<MISSING>"

    return latitude, longitude


def fetch_data():
    out = []
    locator_domain = "https://www.liquorexpress.ca/"
    api = "https://www.liquorexpress.ca/locations/"

    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    r = session.get(api, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@class='location-container']")

    for d in divs:
        location_name = "".join(d.xpath("./preceding-sibling::h3[1]/text()")).strip()
        page_url = "".join(d.xpath(".//a[contains(@href, '/locations/')]/@href"))
        if not page_url:
            page_url = api
        if page_url.startswith("/"):
            page_url = f"https://www.liquorexpress.ca{page_url}"

        line = "".join(
            d.xpath(
                ".//td[contains(text(), 'Location:')]/following-sibling::td[1]/text()"
            )
        ).strip()

        adr = parse_address(International_Parser(), line)
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
        phone = "".join(
            d.xpath(
                ".//td[contains(text(), 'Contact')]/following-sibling::td[1]/span[contains(text(), 'Ph')]/following-sibling::text()[1]"
            )
        ).strip()
        text = "".join(d.xpath(".//iframe/@src"))
        latitude, longitude = get_coords_from_embed(text)
        location_type = "<MISSING>"
        hours_of_operation = "".join(
            d.xpath(".//td[contains(text(), 'Hours')]/following-sibling::td[1]/text()")
        ).strip()

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
