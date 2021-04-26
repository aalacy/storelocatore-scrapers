import csv

from lxml import html
from sgrequests import SgRequests
from sgscrape.sgpostal import International_Parser, parse_address


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


def get_urls():
    session = SgRequests()
    r = session.get("http://www.littlechef.co.uk/locations/")
    tree = html.fromstring(r.text)

    return tree.xpath("//div[@class='location']/a/@href")


def get_row(page_url):
    locator_domain = "http://www.littlechef.co.uk/"
    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = tree.xpath("//h1[@class='ribbon']/text()")[0].strip()
    line = (
        "".join(
            tree.xpath(
                "//p[./strong[contains(text(), 'Address')]]/following-sibling::p[1]/text()|//p[./strong[contains(text(), 'Address')]]/text()"
            )
        )
        .replace("Little Chef", "")
        .strip()
    )

    if "." in line:
        postal = line.split(".")[-1].strip()
        line = line.split(".")[0].strip()
    else:
        postal = " ".join(line.split()[-2:])
        line = line.replace(postal, "").strip()
        if line.endswith(","):
            line = line[:-1]

    adr = parse_address(International_Parser(), line, postcode=postal)

    street_address = (
        f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
            "None", ""
        ).strip()
        or "<MISSING>"
    )
    city = adr.city or "<MISSING>"
    state = adr.state or "<MISSING>"
    postal = adr.postcode or "<MISSING>"
    if city == "<MISSING>" and "Shrewsbury" in location_name:
        city = "Bayston Hill"
        street_address = street_address.replace(city, "").strip()

    country_code = "GB"
    store_number = "<MISSING>"
    phone = (
        "".join(
            tree.xpath("//p[./strong[contains(text(), 'Telephone')]]/strong/text()")
        )
        .replace("Telephone:", "")
        .strip()
        or "<MISSING>"
    )
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    location_type = "<MISSING>"
    hours = []
    tags = tree.xpath("//div[./p/strong[contains(text(), 'OPENING')]]/p/*")
    for t in tags:
        if "".join(t.xpath("./text()")).find("OPENING") != -1:
            continue

        if t.tag == "strong":
            hours.append("".join(t.xpath(".//text()")).strip())
        elif t.tag == "br":
            hours.append(";")
    hours_of_operation = "".join(hours).replace("\n", ";") or "<MISSING>"

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

    return row


def fetch_data():
    out = []
    urls = get_urls()
    for u in urls:
        row = get_row(u)
        out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
