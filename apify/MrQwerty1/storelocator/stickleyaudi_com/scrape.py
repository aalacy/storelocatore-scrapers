import csv

from concurrent import futures
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


def get_urls():
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    r = session.get("https://shopstickley.com/locations/", headers=headers)
    tree = html.fromstring(r.text)

    return tree.xpath("//p/a[contains(@href, '/locations/')]/@href")


def get_data(page_url):
    locator_domain = "https://shopstickley.com/"

    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    location_name = "Stickley Furniture"
    line = tree.xpath(
        "//*[./b[contains(text(), 'ADDRESS:')]]/text()|//*[./strong[contains(text(), 'ADDRESS:')]]/text()"
    )
    line = list(filter(None, [l.strip() for l in line]))

    street_address = " ".join(line[:-1])
    if "Plaza" in street_address:
        street_address = street_address.split("Plaza")[1].strip()
    line = line[-1].replace(" US", "")
    city = line.split(",")[0].strip()
    if "(" in city:
        city = city.split("(")[0].strip()
    line = line.split(",")[1].strip()
    state = line.split()[0]
    postal = line.split()[1]
    country_code = "US"
    store_number = "<MISSING>"
    phone = (
        "".join(
            tree.xpath(
                "//p[./*[contains(text(), 'PHONE:')]]/a/text()|//p[./*[contains(text(), 'PHONE:')]]/text()"
            )
        ).strip()
        or "<MISSING>"
    )

    text = "".join(tree.xpath("//iframe/@src"))
    latitude, longitude = get_coords_from_embed(text)
    location_type = "<MISSING>"

    _tmp = []
    hours = tree.xpath(
        "//p[./strong[contains(text(), 'HOURS')]]/text()|//p[./b[contains(text(), 'HOURS')]]/text()"
    )

    for h in hours:
        h = h.strip()
        if h.endswith(":"):
            h += " Closed"
        _tmp.append(h)

    hours_of_operation = ";".join(_tmp) or "Temporarily Closed"

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
