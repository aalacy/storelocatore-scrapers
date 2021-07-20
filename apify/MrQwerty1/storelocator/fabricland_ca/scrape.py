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
    urls = []
    r = session.get("https://fabricland.ca/sitemap.xml")
    tree = html.fromstring(r.content)

    for u in tree.xpath("//loc[contains(text(), 'storelocator')]/text()"):
        if u.count("/") == 6:
            urls.append(u)

    return urls


def get_coords_from_embed(text):
    try:
        latitude = text.split("!3d")[1].strip().split("!")[0].strip()
        longitude = text.split("!2d")[1].strip().split("!")[0].strip()
    except IndexError:
        latitude, longitude = "<MISSING>", "<MISSING>"

    return latitude, longitude


def get_data(page_url):
    locator_domain = "https://fabricland.ca/"
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//title/text()")).split("Store")[0].strip()
    line = (
        "".join(tree.xpath("//h3[./b[contains(text(), ',')]][1]//text()"))
        .replace("Fabricland,", "")
        .strip()
    )
    if not line:
        return

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
    phone = "".join(tree.xpath("//h3/b/a/text()")).strip() or "<MISSING>"
    text = "".join(tree.xpath("//iframe/@src"))
    latitude, longitude = get_coords_from_embed(text)
    location_type = "<MISSING>"

    _tmp = []
    hours = tree.xpath(
        "//div[./b[text()='Hours']]/following-sibling::h4[not(./a)]/text()|//b[text()='Hours']/following-sibling::h4[not(./a)]/text()"
    )
    black = ["July", "statutory", "law", "Holiday Hours", "Easter", "Due"]
    for h in hours:
        for b in black:
            if b in h:
                break
        else:
            _tmp.append(h.strip())

    hours_of_operation = ";".join(_tmp) or "<MISSING>"

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
    session = SgRequests()
    scrape()
