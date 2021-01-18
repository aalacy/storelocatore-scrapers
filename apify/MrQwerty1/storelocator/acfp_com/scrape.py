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
    r = session.get("https://acfp.com/acfp_location-sitemap.xml")
    tree = html.fromstring(r.content)

    return tree.xpath("//loc/text()")


def get_data(page_url):
    locator_domain = "https://acfp.com/"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//div[@class='location-title']/text()")).strip()
    line = tree.xpath("//div[@class='address formatted']/p")[-1].xpath("./text()")
    line = list(filter(None, [l.strip() for l in line]))

    street_address = line[0]

    if street_address.find("(") != -1:
        street_address = street_address.split("(")[0].strip()
    if street_address.endswith(","):
        street_address = street_address[:-1]
    line = line[-1]
    city = line.split(",")[0].strip()
    line = line.split(",")[1].strip()
    state = line.split()[0]
    postal = line.split()[1]
    if postal.find(".") != -1:
        postal = postal.split(".")[0]
    country_code = "US"
    store_number = "<MISSING>"
    phone = (
        "".join(tree.xpath("//a[@class='phone font-weight-bold']/text()")).strip()
        or "<MISSING>"
    )
    latitude = "".join(tree.xpath("//div[@data-lat]/@data-lat")) or "<MISSING>"
    longitude = "".join(tree.xpath("//div[@data-lat]/@data-lng")) or "<MISSING>"
    location_type = "<MISSING>"
    hours_of_operation = (
        "".join(tree.xpath("//div[@class='hours formatted']/p//text()")).strip()
        or "<MISSING>"
    )

    check = "".join(tree.xpath("//div[@class='address formatted']/p/text()"))
    if check.find("soon") != -1:
        hours_of_operation = "Coming Soon"

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
