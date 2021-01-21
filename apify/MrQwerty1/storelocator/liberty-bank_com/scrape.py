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
    r = session.get("https://www.liberty-bank.com/locations")
    tree = html.fromstring(r.text)

    return tree.xpath("//a[@class='branch-link']/@href")


def get_data(url):
    locator_domain = "https://www.liberty-bank.com/"
    page_url = f"https://www.liberty-bank.com{url}"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    line = tree.xpath("//label[@class='sfLocation']")[0]
    location_name = "".join(line.xpath("./@data-title")) or "<MISSING>"
    street_address = "".join(line.xpath("./@data-street")) or "<MISSING>"
    city = "".join(line.xpath("./@data-city")) or "<MISSING>"
    state = "".join(line.xpath("./@data-state")) or "<MISSING>"
    postal = "".join(line.xpath("./@data-zip")) or "<MISSING>"
    country_code = "US"
    store_number = "<MISSING>"
    phone = (
        "".join(
            tree.xpath(
                "//ul/li[contains(text(), 'Branch')]/a[contains(@href, 'tel')]/text()"
            )
        ).strip()
        or "<MISSING>"
    )
    latitude = "".join(line.xpath("./@data-latitude")) or "<MISSING>"
    longitude = "".join(line.xpath("./@data-longitude")) or "<MISSING>"
    location_type = "Branch"

    _tmp = []
    days = tree.xpath(
        "//table[@style='margin-bottom: 15px;']//td[.//h4[contains(text(), 'Day')]]//li/text()"
    )[2:]
    times = tree.xpath(
        "//table[@style='margin-bottom: 15px;']//td[.//h4[contains(text(), 'Lobby')]]//li/text()"
    )[2:]
    for d, t in zip(days, times):
        _tmp.append(f"{d.strip()}: {t.strip()}")

    hours_of_operation = ";".join(_tmp) or "<MISSING>"

    if location_name.lower().find("closed") != -1:
        hours_of_operation = "Closed"
    elif location_name.find("ATM") != -1:
        location_type = "ATM"
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
