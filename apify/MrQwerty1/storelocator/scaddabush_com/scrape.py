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


def get_urls():
    session = SgRequests()
    r = session.get("https://www.scaddabush.com/locations/")
    tree = html.fromstring(r.text)

    return tree.xpath(
        "//a[@class='locationsbutton' and not(contains(@href, '/promotions'))]/@href"
    )


def get_coords_from_embed(text):
    try:
        latitude = text.split("!3d")[1].strip().split("!")[0].strip()
        longitude = text.split("!2d")[1].strip().split("!")[0].strip()
    except IndexError:
        latitude, longitude = "<MISSING>", "<MISSING>"

    return latitude, longitude


def get_data(page_url):
    locator_domain = "https://www.scaddabush.com/"
    if page_url.startswith("/"):
        page_url = f"https://www.scaddabush.com{page_url}"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = tree.xpath("//h1/text()")[0].strip()
    line = tree.xpath(
        "//h4[contains(text(), 'Information')]/following-sibling::p[1]/text()"
    )
    line = list(filter(None, [l.strip() for l in line]))

    postal = line.pop()
    street_address = line.pop(0)
    if street_address.endswith(","):
        street_address = street_address[:-1]
    line = line[-1]
    city = line.split(",")[0].strip()
    state = line.split(",")[1].strip()
    country_code = "CA"
    store_number = "<MISSING>"
    phone = (
        "".join(
            tree.xpath(
                "//h4[contains(text(), 'Information')]/following-sibling::p/a/text()"
            )
        ).strip()
        or "<MISSING>"
    )
    text = "".join(tree.xpath("//iframe/@src"))
    latitude, longitude = get_coords_from_embed(text)
    location_type = "<MISSING>"
    hours_of_operation = (
        " ".join(
            " ".join(
                tree.xpath(
                    "//p[./strong[contains(text(), 'PATIO')]]/following-sibling::p[1]//text()"
                )
            ).split()
        )
        or "<MISSING>"
    )
    hours_of_operation = hours_of_operation.replace("pm F", "pm;F")

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
