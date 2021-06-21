import csv

from concurrent import futures
from datetime import datetime
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
    r = session.get("https://suitsupply.com/en-ua/stores?country=US")
    tree = html.fromstring(r.text)

    return tree.xpath("//a[@class='store__block store__link']/@href")


def get_data(url):
    locator_domain = "https://suitsupply.com/"
    page_url = f"https://suitsupply.com{url}"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(
        tree.xpath("//h2[@class='store-details__store-name']/text()")
    ).strip()
    street_address = (
        ", ".join(
            tree.xpath("//span[@class='store-details__address-line'][1]/text()")
        ).strip()
        or "<MISSING>"
    )
    line = "".join(
        tree.xpath("//span[@class='store-details__address-line'][2]/text()")
    ).strip()
    city = " ".join(line.split()[:-2])
    state = line.split()[-2]
    if state == "York":
        city = "New York"
        state = "NY"
    postal = line.split()[-1]
    country_code = "US"
    store_number = "<MISSING>"
    phone = (
        "".join(
            tree.xpath(
                "//div[@class='store-details__contact-holder']/a[contains(@href, 'tel:')]/text()"
            )
        ).strip()
        or "<MISSING>"
    )

    text = "".join(tree.xpath("//a[contains(@class, 'location-link')]/@href"))
    if text:

        latitude = text.split("@")[1].split(",")[0]
        longitude = text.split("@")[1].split(",")[1]
    else:
        latitude, longitude = "<MISSING>", "<MISSING>"
    location_type = "<MISSING>"

    _tmp = []
    days = tree.xpath("//span[@class='store-hours__text store-hours__day-name']/text()")
    times = tree.xpath(
        "//span[@class='store-hours__text store-hours__day-hours']/text()"
    )

    for d, t in zip(days, times):
        _tmp.append(f"{d.strip()}: {t.strip()}")

    today = datetime.today().strftime("%A")
    hours_of_operation = ";".join(_tmp).replace("Today", today) or "<MISSING>"

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
