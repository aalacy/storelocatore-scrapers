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


def get_states():
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Accept": "*/*",
        "Accept-Language": "uk-UA,uk;q=0.8,en-US;q=0.5,en;q=0.3",
        "X-Moz": "prefetch",
        "Connection": "keep-alive",
        "Referer": "https://www.alwaysbestcare.com/locations/?srchtype=state&srch=CA",
        "TE": "Trailers",
    }
    r = session.get("https://www.alwaysbestcare.com/locations/", headers=headers)
    tree = html.fromstring(r.text)

    return tree.xpath("//div[@class='locationlist']/ul/li/a/@href")


def get_urls():
    urls = []
    states = get_states()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Accept": "*/*",
        "Accept-Language": "uk-UA,uk;q=0.8,en-US;q=0.5,en;q=0.3",
        "X-Moz": "prefetch",
        "Connection": "keep-alive",
        "Referer": "https://www.alwaysbestcare.com/locations/?srchtype=state&srch=CA",
        "TE": "Trailers",
    }
    session = SgRequests()

    for state in states:
        r = session.get(state, headers=headers)
        tree = html.fromstring(r.text)
        urls += tree.xpath(
            "//div[@id='resultstop']/ul/li/p/a[text()='Click here']/@href"
        )

    return set(urls)


def get_coords_from_google_url(url):
    try:
        if url.find("ll=") != -1:
            latitude = url.split("ll=")[1].split(",")[0]
            longitude = url.split("ll=")[1].split(",")[1].split("&")[0]
        else:
            latitude = url.split("@")[1].split(",")[0]
            longitude = url.split("@")[1].split(",")[1]
    except IndexError:
        latitude, longitude = "<MISSING>", "<MISSING>"

    return latitude, longitude


def get_data(page_url):
    locator_domain = "https://www.alwaysbestcare.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Accept": "*/*",
        "Accept-Language": "uk-UA,uk;q=0.8,en-US;q=0.5,en;q=0.3",
        "X-Moz": "prefetch",
        "Connection": "keep-alive",
        "Referer": "https://www.alwaysbestcare.com/locations/?srchtype=state&srch=CA",
        "TE": "Trailers",
    }

    session = SgRequests()
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    location_name = (
        tree.xpath("//h1//text()|//h3/span/strong/text()|//h3/span/text()")[0]
        .replace("Welcome to", "")
        .strip()
    )
    street_address = (
        " ".join(
            "".join(tree.xpath("//span[@itemprop='streetAddress']/text()")).split()
        )
        or "<MISSING>"
    )
    city = (
        "".join(tree.xpath("//span[@itemprop='addressLocality']/text()")).strip()
        or "<MISSING>"
    )
    state = (
        "".join(tree.xpath("//span[@itemprop='addressRegion']/text()")).strip()
        or "<MISSING>"
    )
    postal = (
        "".join(tree.xpath("//span[@itemprop='postalCode']/text()")).strip()
        or "<MISSING>"
    )
    country_code = "US"
    store_number = "<MISSING>"
    phone = (
        "".join(tree.xpath("//strong[contains(text(), 'Call Us:')]/text()"))
        .replace("Call Us:", "")
        .strip()
        or "<MISSING>"
    )
    text = "".join(tree.xpath("//a[contains(@href, 'google')]/@href"))
    latitude, longitude = get_coords_from_google_url(text)
    location_type = "<MISSING>"
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
    s = set()
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url): url for url in urls}
        for future in futures.as_completed(future_to_url):
            row = future.result()
            if row:
                _id = row[3]
                if _id not in s:
                    s.add(_id)
                    out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
