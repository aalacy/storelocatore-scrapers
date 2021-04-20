import csv

from concurrent import futures
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


def get_urls():
    session = SgRequests()
    r = session.get("https://www.scottishgolfcourses.com/atoz.html")
    tree = html.fromstring(r.text)

    return tree.xpath("//div[@class='col-sm-4']/a/@href")


def get_data(url):
    locator_domain = "hhttps://www.scottishgolfcourses.com/"
    page_url = f"https://www.scottishgolfcourses.com{url}"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//h1/text()")).strip()
    text = "".join(tree.xpath("//h1/following-sibling::*/text()")).strip()
    line = text.split("Address:")[-1].strip()
    if line.endswith(","):
        line = line[:-1].strip()
    postal = " ".join(line.split()[-2:])
    if "," not in postal:
        line = line.replace(postal, "")
        adr = parse_address(International_Parser(), line, postcode=postal)
    else:
        adr = parse_address(International_Parser(), line)

    street_address = (
        f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
            "None", ""
        ).strip()
        or "<MISSING>"
    )

    if street_address == "<MISSING>":
        street_address = location_name

    city = adr.city or "<MISSING>"
    state = adr.state or "<MISSING>"
    postal = adr.postcode or "<MISSING>"
    country_code = "GB"
    store_number = "<MISSING>"
    phone = (
        "".join(
            tree.xpath(
                "//strong[contains(text(), 'Telephone')]/following-sibling::text()"
            )
        )
        .replace("N/A", "")
        .strip()
        or "<MISSING>"
    )
    if "/" in phone:
        phone = phone.split("/")[0].strip()
    if "ext" in phone:
        phone = phone.split("ext")[0].strip()

    latitude = "<MISSING>"
    longitude = "<MISSING>"
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

    return row


def fetch_data():
    out = []
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url): url for url in urls}
        for future in futures.as_completed(future_to_url):
            row = future.result()
            if row:
                out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
