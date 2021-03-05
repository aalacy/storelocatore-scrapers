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
    urls = []
    session = SgRequests()

    start_urls = [
        "https://meeks.com/midwest/locations/",
        "https://meeks.com/western/store-locations/",
    ]
    for u in start_urls:
        r = session.get(u)
        tree = html.fromstring(r.text)
        urls += tree.xpath("//div[@class='right' or @id='primary-content']//a/@href")

    return urls


def parse_western(tree, page_url):
    locator_domain = "https://meeks.com/"

    location_name = "MEEKS"
    line = tree.xpath("//address/text()")
    line = list(filter(None, [l.strip() for l in line]))

    try:
        street_address = ", ".join(line[:-2])
        postal = line[-1]
        line = line[-2]
        city = line.split(",")[0].strip()
        state = line.split(",")[-1].strip()
    except IndexError:
        street_address = "<MISSING>"
        city = line[0].split(",")[0].strip()
        state = line[0].split(",")[-1].strip()
        postal = "<MISSING>"
    country_code = "US"
    store_number = "<MISSING>"
    phone = (
        "".join(tree.xpath("//p[contains(text(), 'Phone:')]/text()"))
        .replace("Phone:", "")
        .strip()
        or "<MISSING>"
    )
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    location_type = "<MISSING>"
    hours_of_operation = (
        " ".join(
            ";".join(
                tree.xpath("//div[@class='hours']/p[contains(text(), ':')]/text()")
            ).split()
        ).strip()
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

    return row


def parse_midwest(tree, page_url):
    locator_domain = "https://meeks.com/"

    location_name = "MEEKS"
    line = tree.xpath("//div[@class='address']/text()")
    line = list(filter(None, [l.strip() for l in line]))

    street_address = ", ".join(line[:-2])
    postal = line[-1]
    line = line[-2]
    city = line.split(",")[0].strip()
    state = line.split(",")[-1].strip()
    country_code = "US"
    store_number = "<MISSING>"
    try:
        phone = tree.xpath("//div[@class='phone']//dd/text()")[0] or "<MISSING>"
    except IndexError:
        phone = "<MISSING>"

    text = "".join(
        tree.xpath("//script[contains(text(), 'var longitude')]/text()")
    ).strip()
    latitude = text.split("latitude  = ")[1].split(",")[0].replace("'", "").strip()
    longitude = text.split("longitude = ")[1].split(",")[0].replace("'", "").strip()
    location_type = "<MISSING>"
    hours_of_operation = (
        " ".join(
            ";".join(
                tree.xpath(
                    "//div[@class='hours-of-operation']/p[contains(text(), ':')]/text()"
                )
            ).split()
        ).strip()
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

    return row


def get_data(url):
    page_url = f"https://meeks.com{url}"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    if page_url.find("/western") != -1:
        row = parse_western(tree, page_url)
    else:
        row = parse_midwest(tree, page_url)

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
