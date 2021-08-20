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
    locator_domain = "https://freshcitykitchen.com/"
    page_url = "https://freshcitykitchen.com/pages/retail"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@data-pf-type='Column' and .//iframe]")

    for d in divs:
        location_name = "".join(d.xpath(".//span/span[1]/text()")).strip()
        line = d.xpath(".//span[./span]/text()")
        line = list(filter(None, [l.strip() for l in line]))
        phone = line.pop()
        csz = line.pop()

        street_address = ", ".join(line)
        city = csz.split(",")[0].strip()
        csz = csz.split(",")[1].strip()
        state = csz.split()[0]
        postal = csz.split()[1]
        country_code = "US"
        store_number = "<MISSING>"

        text = "".join(d.xpath(".//iframe/@src"))
        latitude, longitude = get_coords_from_embed(text)
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
