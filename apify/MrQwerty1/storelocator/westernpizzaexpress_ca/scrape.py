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


def get_coords_from_embed(text):
    try:
        latitude = text.split("!3d")[1].strip().split("!")[0].strip()
        longitude = text.split("!2d")[1].strip().split("!")[0].strip()
    except IndexError:
        latitude, longitude = "<MISSING>", "<MISSING>"

    return latitude, longitude


def fetch_data():
    out = []
    locator_domain = "https://westernpizzaexpress.ca/"
    page_url = "https://westernpizzaexpress.ca/locations/"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@class='location-box']")

    for d in divs:
        location_name = "".join(
            d.xpath("./h2//text()|./h2/following-sibling::p[1]/text()")
        ).strip()
        line = d.xpath("./div[1]/p/text()")
        line = list(filter(None, [l.strip() for l in line]))

        street_address = line[0]
        line = line[-1]
        if "\xa0" not in line:
            divider = "•"
        else:
            divider = "\xa0"

        city = line.split(divider)[0].strip()
        state = line.split(divider)[-1].strip()
        postal = "<MISSING>"
        country_code = "CA"
        store_number = "<MISSING>"
        phone = (
            "".join(d.xpath(".//a[contains(@href, 'tel')]/@href")).replace("tel:", "")
            or "<MISSING>"
        )
        text = "".join(d.xpath(".//iframe/@src"))
        latitude, longitude = get_coords_from_embed(text)
        location_type = "<MISSING>"
        hours_of_operation = (
            " ".join(";".join(d.xpath(".//small/text()")).split())
            .replace("; ;", "")
            .replace("•", "")
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
