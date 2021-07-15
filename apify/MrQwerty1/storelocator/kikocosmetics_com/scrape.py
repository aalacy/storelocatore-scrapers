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
    r = session.get(
        "https://www.kikocosmetics.com/eshop/storelocator/all", cookies=cookies
    )
    js = r.json()["features"]

    for j in js:
        slug = j["properties"]["url"]
        urls.append(f"https://www.kikocosmetics.com{slug}")

    return urls


def get_data(page_url):
    locator_domain = "https://www.kikocosmetics.com/"

    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//h1[@itemprop='name']/text()")[-1]).strip()
    try:
        street_address = tree.xpath("//span[@itemprop='streetAddress']/text()")[
            -1
        ].strip()
    except IndexError:
        street_address = "<MISSING>"
    try:
        city = tree.xpath("//span[@itemprop='addressLocality']/text()")[-1].strip()
    except IndexError:
        city = "<MISSING>"
    state = "<MISSING>"
    try:
        postal = tree.xpath("//span[@itemprop='postalCode']/text()")[-1].strip()
    except IndexError:
        postal = "<MISSING>"
    try:
        country_code = tree.xpath("//span[@itemprop='addressCountry']/text()")[
            -1
        ].strip()
    except IndexError:
        country_code = "<MISSING>"
    store_number = "<MISSING>"
    try:
        phone = tree.xpath("//span[@itemprop='telephone']/text()")[-1].strip()
    except IndexError:
        phone = "<MISSING>"
    try:
        latitude = tree.xpath("//meta[@itemprop='latitude']/@content")[-1]
    except IndexError:
        latitude = "<MISSING>"
    try:
        longitude = tree.xpath("//meta[@itemprop='longitude']/@content")[-1]
    except IndexError:
        longitude = "<MISSING>"
    location_type = "<MISSING>"
    hours_of_operation = (
        ";".join(tree.xpath("//dl[@itemprop='openingHours']/@content")) or "<MISSING>"
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
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "uk-UA,uk;q=0.8,en-US;q=0.5,en;q=0.3",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }

    cookies = {"JSESSIONID": "106A7FDD2F65FC200D2625B658ECD4A4"}

    scrape()
