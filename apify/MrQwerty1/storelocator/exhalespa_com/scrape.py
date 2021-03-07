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
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0"
    }
    r = session.get("https://www.exhalespa.com/locations", headers=headers)
    tree = html.fromstring(r.text)

    return tree.xpath("//div[@class='loc-locations']//li/a/@href")


def get_data(url):
    locator_domain = "https://www.exhalespa.com/"
    page_url = f"https://www.exhalespa.com{url}"
    if "virtual-" in page_url or "bermuda" in page_url:
        return

    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0"
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    location_name = "".join(
        tree.xpath("//h1/text()|//div[@class='location_banner']//h2/text()")
    ).strip()
    line = tree.xpath("//div[@class='address']/p/text()")
    line = list(filter(None, [l.strip() for l in line]))

    street_address = ", ".join(line[:-1]).strip() or "<MISSING>"
    line = line[-1]
    city = line.split(",")[0].strip()
    line = line.split(",")[1].strip()
    state = line.split()[0]
    postal = line.split()[1]
    country_code = "US"
    store_number = "<MISSING>"
    phone = (
        "".join(tree.xpath("//span[@class='phone']/a/text()")).strip() or "<MISSING>"
    )
    latitude = (
        "".join(tree.xpath("//meta[@property='latitude']/@content")) or "<MISSING>"
    )
    longitude = (
        "".join(tree.xpath("//meta[@property='longitude']/@content")) or "<MISSING>"
    )
    location_type = "<MISSING>"

    _tmp = []
    days = tree.xpath("//div[@class='text']")[0].xpath(
        ".//p/strong/text()|.//span/strong/text()"
    )
    times = tree.xpath("//div[@class='text']")[0].xpath(".//p/text()|.//span/text()")
    times = list(filter(None, [t.strip() for t in times]))

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
