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
        latitude = text.split("!1d")[1].strip().split("!")[0].strip()
        longitude = text.split("!2d")[1].strip().split("!")[0].strip()
    except IndexError:
        latitude = text.split("@")[1].split(",")[0]
        longitude = text.split("@")[1].split(",")[1]

    return latitude, longitude


def get_coords(page_url):
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//iframe/@src"))
    if "!1d" not in text:
        text = "".join(tree.xpath("//a[@class='open-map']/@href"))

    return get_coords_from_embed(text)


def fetch_data():
    out = []
    locator_domain = "https://www.daysjewelers.com/"
    api = "https://www.daysjewelers.com/about-us/our-stores"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    r = session.get(api, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@class='locations__single-location']")

    for d in divs:
        location_name = "".join(d.xpath("./h3/text()")).strip()
        page_url = "".join(d.xpath(".//a[@class='button white']/@href"))
        if "corporate" in page_url or "credit" in page_url:
            continue
        line = d.xpath("./p[1]/text()")
        line = list(filter(None, [l.strip() for l in line]))
        street_address = line.pop(0)
        line = line[-1]
        city = line.split(",")[0].strip()
        line = line.split(",")[1].strip()
        state = line.split()[0]
        postal = line.split()[1]
        country_code = "US"
        store_number = location_name.split("#")[1].split()[0]
        phone = (
            "".join(d.xpath(".//a[contains(@href, 'tel:')]/text()")).strip()
            or "<MISSING>"
        )
        latitude, longitude = get_coords(page_url)
        location_type = "<MISSING>"
        hours = d.xpath(".//p[./b[contains(text(), 'Hours')]]/text()")
        hours = list(filter(None, [h.strip() for h in hours]))
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
    session = SgRequests()
    scrape()
