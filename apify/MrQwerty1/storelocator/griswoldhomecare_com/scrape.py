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


def get_states():
    session = SgRequests()
    r = session.get("https://www.griswoldhomecare.com/sitemap.xml")
    tree = html.fromstring(r.content)

    return tree.xpath(
        "//loc[contains(text(), 'https://www.griswoldhomecare.com/locations/')]/text()"
    )


def get_urls():
    urls = []
    session = SgRequests()
    states = get_states()
    states.remove("https://www.griswoldhomecare.com/locations/")
    for state in states:
        r = session.get(state)
        tree = html.fromstring(r.text)
        urls += tree.xpath("//li[@class='third']/a[1]/@href")

    return urls


def get_data(url):
    locator_domain = "https://www.griswoldhomecare.com/"
    page_url = f"https://www.griswoldhomecare.com{url}"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = " ".join("".join(tree.xpath("//h1/text()")).split())
    if not location_name:
        return

    street_address = (
        " ".join(
            ", ".join(tree.xpath("//span[@itemprop='streetAddress']/text()")).split()
        )
        or "<MISSING>"
    )
    city = (
        "".join(tree.xpath("//span[@itemprop='addressLocality']/text()"))
        .replace(",", "")
        .strip()
        or "<MISSING>"
    )
    state = (
        "".join(tree.xpath("//span[@itemprop='addressRegion']/text()")).strip()
        or "<MISSING>"
    )
    postal = (
        "".join(tree.xpath("//span[@itemprop='postalCode']/text()")).strip()
        or "<MISSING>"
    )
    if len(postal) == 4:
        postal = f"0{postal}"
    country_code = "US"
    store_number = "".join(tree.xpath("//body/@data-location")) or "<MISSING>"
    try:
        phone = (
            tree.xpath("//a[@id='LocalFooter_3']/@href|//a[@class='phone']/@href")[0]
            .replace("tel:", "")
            .strip()
        )
    except IndexError:
        phone = "<MISSING>"
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
