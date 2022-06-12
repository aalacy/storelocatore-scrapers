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


def translate(hours):
    hours = (
        hours.replace("à", "to")
        .replace(" au ", " - ")
        .replace(" et ", " - ")
        .replace("h00", ":00")
        .replace("Dimanche", "Sunday")
        .replace("Lundi", "Monday")
        .replace("Mardi", "Tuesday")
        .replace("Mercredi", "Wednesday")
        .replace("Jeudi", "Thursday")
        .replace("Vendredi", "Friday")
        .replace("Samedi", "Saturday")
    )
    return hours


def fetch_data():
    out = []
    locator_domain = "https://restaurantnormandin.com/"
    page_url = "https://restaurantnormandin.com/trouver-un-restaurant/"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@class='restaurant-item']")

    for d in divs:
        location_name = "".join(
            d.xpath(".//div[@class='block']/span[@class='title -small']/text()")
        ).strip()
        line = "".join(d.xpath(".//span[@class='address']/text()")).strip()
        if not line or line == "-":
            continue

        adr = parse_address(International_Parser(), line)
        street_address = (
            f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
                "None", ""
            ).strip()
            or "<MISSING>"
        )

        city = adr.city or "<MISSING>"
        if city == "<MISSING>":
            city = location_name
        if city == "Donnacona":
            street_address = line.split(", Donnacona")[0]
        state = adr.state or "<MISSING>"
        postal = adr.postcode or "<MISSING>"
        country_code = "CA"
        store_number = "<MISSING>"
        phone = (
            "".join(d.xpath(".//a[@class='phone']/span/text()")).strip() or "<MISSING>"
        )
        latitude = (
            "".join(d.xpath(".//span[@class='resto-lat']/text()")).strip()
            or "<MISSING>"
        )
        longitude = (
            "".join(d.xpath(".//span[@class='resto-long']/text()")).strip()
            or "<MISSING>"
        )
        location_type = "<MISSING>"
        hours_of_operation = (
            translate(
                ";".join(
                    d.xpath(
                        ".//span[text()='Comptoir']/following-sibling::ul[1]/li/text()"
                    )
                )
            )
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
