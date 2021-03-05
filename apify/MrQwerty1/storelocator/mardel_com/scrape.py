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
    r = session.get("https://www.mardel.com/stores")
    tree = html.fromstring(r.text)
    states = tree.xpath("//a[contains(@href, '/stores?state=')]/@href")
    for s in states:
        r = session.get(f"https://www.mardel.com{s}")
        tree = html.fromstring(r.text)
        links = tree.xpath("//a[contains(@href, '/stores/search/')]/@href")
        for l in links:
            urls.append(f"https://www.mardel.com{l}")

    return urls


def get_data(page_url):
    locator_domain = "https://www.mardel.com/"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    street_address = (
        "".join(tree.xpath("//ul[@class='address']/li[1]/text()")).strip()
        or "<MISSING>"
    )
    line = "".join(tree.xpath("//ul[@class='address']/li[2]/text()")).strip()
    city = line.split(",")[0].strip()
    line = line.split(",")[1].strip()
    state = line.split()[0]
    postal = line.split()[-1]
    country_code = "US"
    store_number = page_url.split("/")[-1]
    phone = (
        "".join(tree.xpath("//ul[@class='address']/li[3]/text()")).strip()
        or "<MISSING>"
    )
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    location_type = "<MISSING>"
    location_name = f"Store #{store_number} - {city}, {state}"

    _tmp = []
    days = tree.xpath("//td[@class='weekday-openings-day']/text()")
    times = tree.xpath("//td[@class='weekday-openings-times text-right']/text()")

    for d, t in zip(days, times):
        _tmp.append(f"{d.strip()} {t.strip()}")

    hours_of_operation = ";".join(_tmp) or "<MISSING>"

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
