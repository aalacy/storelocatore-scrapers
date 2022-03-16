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


def get_coords(text):
    text = text.replace("://", "")
    if "//" in text:
        return text.split("//")[-1].split(",")
    else:
        return text.split("@")[1].split(",")[:2]


def get_urls():
    session = SgRequests()
    r = session.get("https://www.wownewengland.com/")
    tree = html.fromstring(r.text)

    return set(
        tree.xpath("//a[text()='CLUB LOCATIONS']/following-sibling::ul//a/@href")
    )


def get_data(page_url):
    locator_domain = "https://www.wownewengland.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    }

    session = SgRequests()
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//title/text()")).split("-")[0].strip()
    line = tree.xpath("//div[@class='elementor-widget-container']/p[1]//text()")
    line = list(filter(None, [l.strip() for l in line]))[:3]

    phone = line[2]
    street_address = line[0]
    line = line[1]
    postal = line.split()[-1]
    state = line.split()[-2]
    city = line.replace(postal, "").replace(state, "").replace(",", "").strip()
    country_code = "US"
    store_number = "<MISSING>"

    text = "".join(tree.xpath("//a[contains(@href, 'google')]/@href"))
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    if text:
        latitude, longitude = get_coords(text)

    location_type = "<MISSING>"
    hours = tree.xpath("//p[contains(text(), 'CLUB HOURS')]/text()")
    hours = list(filter(None, [h.strip() for h in hours]))[1:]

    hours_of_operation = ";".join(hours) or "Temporarily Closed"

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
    urls.remove("#")

    with futures.ThreadPoolExecutor(max_workers=1) as executor:
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
