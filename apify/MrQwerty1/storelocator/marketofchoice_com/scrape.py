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
    r = session.get("https://www.marketofchoice.com/locations/")
    tree = html.fromstring(r.text)

    return tree.xpath("//div[./h2]/preceding-sibling::div//a[./img]/@href")


def get_data(page_url):
    locator_domain = "https://www.marketofchoice.com/"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(
        tree.xpath("//div[@class='fusion-column-content']//h1/text()")
    ).strip()
    line = tree.xpath(
        "//div[@class='fusion-column-content']//a[contains(@href, 'maps')]/text()"
    )
    line = list(filter(None, [l.strip() for l in line]))

    street_address = line.pop(0)
    line = "".join(line)
    city = line.split(",")[0].strip()
    line = line.split(",")[1].strip()
    state = line.split()[0]
    postal = line.split()[1]
    country_code = "US"
    store_number = "<MISSING>"
    try:
        phone = tree.xpath(
            "//div[@class='fusion-column-content']//span[@class='fusion-button-text fusion-button-text-left']/text()"
        )[0].strip()
    except IndexError:
        phone = "<MISSING>"
    latitude, longitude = "<MISSING>", "<MISSING>"
    location_type = "<MISSING>"

    hours = tree.xpath(
        "//div[@class='fusion-column-content']//div[.//img[@alt='Open Icon'] and contains(@class, 'fusion-layout-column')]/following-sibling::div[1]//text()"
    )
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

    with futures.ThreadPoolExecutor(max_workers=12) as executor:
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
