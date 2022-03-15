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


def get_coords(text):
    try:
        if text.find("ll=") != -1:
            latitude = text.split("ll=")[1].split(",")[0]
            longitude = text.split("ll=")[1].split(",")[1].split("&")[0]
        else:
            latitude = text.split("@")[1].split(",")[0]
            longitude = text.split("@")[1].split(",")[1]
    except IndexError:
        latitude, longitude = "<MISSING>", "<MISSING>"

    return latitude, longitude


def get_urls():
    session = SgRequests()
    r = session.get("https://www.bathplanet.com/sitemap.xml")
    tree = html.fromstring(r.content)

    return tree.xpath(
        "//loc[contains(text(), '/locator/') and not(contains(text(), '/r-')) and not(text()='https://www.bathplanet.com/locator/')]/text()"
    )


def get_data(page_url):
    locator_domain = "https://www.bathplanet.com/"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//div[@itemprop='address']/h1/text()")).strip()
    street_address = (
        "".join(tree.xpath("//span[@itemprop='streetAddress']/text()"))
        .replace("...", "<MISSING>")
        .strip()
    )
    city = "".join(tree.xpath("//span[@itemprop='addressLocality']/text()")).strip()
    state = "".join(tree.xpath("//span[@itemprop='addressRegion']/text()")).strip()
    postal = "".join(tree.xpath("//span[@itemprop='postalCode']/text()")).strip()
    country_code = "US"
    if len(postal) > 5:
        country_code = "CA"
    store_number = "<MISSING>"
    phone = "".join(tree.xpath("//p[@class='phone']//text()")).strip() or "<MISSING>"
    text = "".join(tree.xpath("//div[@itemprop='address']//a/@href"))
    latitude, longitude = get_coords(text)
    location_type = "<MISSING>"
    hours_of_operation = (
        " ".join(
            "".join(
                tree.xpath("//h5[text()='Hours']/following-sibling::p[1]//text()")
            ).split()
        )
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
