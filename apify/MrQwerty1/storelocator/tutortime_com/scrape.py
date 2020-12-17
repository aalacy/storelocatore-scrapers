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
    r = session.get(
        "https://www.tutortime.com/sitemaps/www-tutortime-com-localschools.xml"
    )
    tree = html.fromstring(r.content)
    return tree.xpath("//loc/text()")


def get_data(page_url):
    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    if r.url != page_url:
        return
    locator_domain = "https://www.tutortime.com/"
    location_name = "".join(tree.xpath("//h1/text()")).strip()
    street_address = (
        "".join(
            tree.xpath("//div[@class='school-info-row']//span[@class='street']/text()")
        ).strip()
        or "<MISSING>"
    )
    line = "".join(
        tree.xpath("//div[@class='school-info-row']//span[@class='cityState']/text()")
    ).strip()
    city = line.split(",")[0].strip() or "<MISSING>"
    line = line.split(",")[1].strip()
    state = line.split()[0].strip()
    postal = line.split()[1].strip()
    country_code = "US"
    store_number = page_url.split("-")[-1].replace("/", "")
    phone = (
        "".join(tree.xpath("//span[@class='localPhone']/text()")).strip() or "<MISSING>"
    )
    location_type = "<MISSING>"
    latitude = (
        "".join(
            tree.xpath(
                "//div[@class='school-info-row']//span[@class='addr']/@data-latitude"
            )
        )
        or "<MISSING>"
    )
    longitude = (
        "".join(
            tree.xpath(
                "//div[@class='school-info-row']//span[@class='addr']/@data-longitude"
            )
        )
        or "<MISSING>"
    )
    hours_of_operation = (
        "".join(tree.xpath("//div[./span[text()='Open:']]/text()")).strip()
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
