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
    r = session.get("https://www.bangor.com/locations")
    tree = html.fromstring(r.text)
    aa = tree.xpath("//a[@class='location-title']")
    for a in aa:
        url = "".join(a.xpath("./@href"))
        if not url:
            slug = "".join(a.xpath("./text()")).strip().lower()
            url = f"/locations/{slug}"

        urls.append(url)

    return urls


def get_data(url):
    locator_domain = "https://www.bangor.com/"
    page_url = f"https://www.bangor.com{url}"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//h1/text()")).strip()
    if location_name.find("ATM") != -1:
        return

    street_address = (
        ", ".join(tree.xpath("//span[@itemprop='streetAddress']/text()")).strip()
        or "<MISSING>"
    )
    if street_address.count(",") > 2:
        street_address = street_address.split(",")[0].strip()

    line = "".join(tree.xpath("//span[@itemprop='addressLocality']/text()")).strip()
    city = line.split(",")[0].strip()
    line = line.split(",")[1].strip()
    state = line.split()[0]
    postal = line.split()[1]
    country_code = "US"
    store_number = "<MISSING>"
    phone = (
        "".join(tree.xpath("//div[@itemprop='telephone']/a/text()")).strip()
        or "<MISSING>"
    )
    latitude = "".join(tree.xpath("//div[@data-lat]/@data-lat")) or "<MISSING>"
    longitude = "".join(tree.xpath("//div[@data-lat]/@data-lng")) or "<MISSING>"
    location_type = "<MISSING>"

    _tmp = []
    if tree.xpath("//div[./div[contains(text(), 'Lobby')]]/div[2]/div/text()"):
        days = tree.xpath("//div[./div[contains(text(), 'Lobby')]]/div[2]/div/text()")
        times = tree.xpath("//div[./div[contains(text(), 'Lobby')]]/div[3]/div/text()")
    else:
        days = tree.xpath("//div[./div[contains(text(), 'Drive')]]/div[2]/div/text()")
        times = tree.xpath("//div[./div[contains(text(), 'Drive')]]/div[3]/div/text()")

    for d, t in zip(days, times):
        _tmp.append(f"{d.strip()}: {t.strip()}")

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
