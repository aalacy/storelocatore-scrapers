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
    r = session.get("http://cathaybank.com/location")
    tree = html.fromstring(r.text)

    return tree.xpath(
        "//div[@class='location-content']//a[contains(@href, 'location')]/@href"
    )


def get_data(url):
    locator_domain = "http://cathaybank.com/"
    page_url = f"http://cathaybank.com{url}"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(
        tree.xpath("//div[@class='location-title-detail']/h3/text()")
    ).strip()
    street_address = (
        "".join(tree.xpath("//span[@class='address-line1']/text()")).strip()
        or "<MISSING>"
    )
    city = (
        "".join(tree.xpath("//span[@class='locality']/text()")).strip() or "<MISSING>"
    )
    state = (
        "".join(tree.xpath("//span[@class='administrative-area']/text()")).strip()
        or "<MISSING>"
    )
    postal = (
        "".join(tree.xpath("//span[@class='postal-code']/text()")).strip()
        or "<MISSING>"
    )
    country_code = "".join(tree.xpath("//span[@class='country']/text()")).strip()
    if country_code == "United States":
        country_code = "US"
    else:
        return
    store_number = "<MISSING>"
    try:
        phone = (
            tree.xpath("//div[contains(text(), 'T ')]/text()")[0]
            .replace("T ", "")
            .strip()
        )
    except IndexError:
        phone = "<MISSING>"
    latitude = (
        "".join(tree.xpath("//meta[@property='latitude']/@content")) or "<MISSING>"
    )
    longitude = (
        "".join(tree.xpath("//meta[@property='longitude']/@content")) or "<MISSING>"
    )
    location_type = "<MISSING>"
    hours_of_operation = (
        "".join(tree.xpath("//div[@class='business-hrs']/div/text()"))
        .strip()
        .replace("\r", "")
        .replace("\n", ";")
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
