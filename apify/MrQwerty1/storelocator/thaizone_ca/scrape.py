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
    locator_domain = "https://thaizone.ca/"
    api_url = "https://thaizone.ca/wp-content/plugins/superstorefinder-wp/ssf-wp-xml.php?wpml_lang=en"
    page_url = "https://thaizone.ca/restaurants/"

    session = SgRequests()
    r = session.get(api_url)
    tree = html.fromstring(r.text)
    items = tree.xpath("//item")

    for i in items:
        line = (
            "".join(i.xpath("./address/text()"))
            .replace("&#39;", "'")
            .replace("&#44;", ",")
        )
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
        location_name = "".join(i.xpath("./location/text()")).replace("&#39;", "'")
        store_number = "".join(i.xpath("./storeid/text()")) or "<MISSING>"
        phone = "".join(i.xpath("./telephone/text()")) or "<MISSING>"
        latitude = "".join(i.xpath("./latitude/text()")) or "<MISSING>"
        longitude = "".join(i.xpath("./longitude/text()")) or "<MISSING>"
        location_type = "<MISSING>"
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
