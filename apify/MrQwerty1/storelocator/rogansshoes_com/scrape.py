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
    r = session.get("https://www.rogansshoes.com/stores")
    tree = html.fromstring(r.text)

    return set(
        tree.xpath(
            "//div[@class='ContentPage Faq']//a[@title and contains(@href,'../')]/@href"
        )
    )


def get_data(url):
    locator_domain = "https://www.rogansshoes.com/"
    page_url = f'https://www.rogansshoes.com{url.replace(".", "")}'

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = tree.xpath("//*[@itemprop='name']/text()")[0].strip()
    street_address = (
        tree.xpath("//*[@itemprop='address']/text()")[0].strip() or "<MISSING>"
    )
    city = (
        tree.xpath("//*[@itemprop='address']/text()")[1].replace(",", "").strip()
        or "<MISSING>"
    )
    state = tree.xpath("//*[@itemprop='address']/text()")[2].strip() or "<MISSING>"
    postal = tree.xpath("//*[@itemprop='address']/text()")[3].strip() or "<MISSING>"
    country_code = "US"
    store_number = "<MISSING>"
    phone = (
        "".join(tree.xpath("//*[@itemprop='telephone']//text()")).strip() or "<MISSING>"
    )
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    location_type = "<MISSING>"

    hours = tree.xpath("//*[@itemprop='openinghours']/text()")
    hours = list(filter(None, [h.strip() for h in hours]))

    hours_of_operation = ";".join(hours) or "<MISSING>"

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
