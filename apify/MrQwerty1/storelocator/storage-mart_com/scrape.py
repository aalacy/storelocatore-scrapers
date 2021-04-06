import csv
import json

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
    start_urls = [
        "https://www.storage-mart.com/sitemap/united-states",
        "https://www.storage-mart.com/sitemap/canada",
        "https://www.storage-mart.com/en-gb/sitemap/united-kingdom",
    ]

    for u in start_urls:
        r = session.get(u)
        tree = html.fromstring(r.text)

        links = tree.xpath(
            "//div[@class='col-xs-5ths']//a[@class='rnl-EditorState-Link']/@href"
        )
        for link in links:
            urls.append(f"https://www.storage-mart.com{link}")

    return urls


def get_data(page_url):
    locator_domain = "https://www.storage-mart.com/"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[contains(text(),'SelfStorage')]/text()"))
    if not text:
        return

    j = json.loads(text)
    location_name = j.get("name")
    a = j.get("address") or {}
    street_address = a.get("streetAddress") or "<MISSING>"
    city = a.get("addressLocality") or "<MISSING>"
    state = a.get("addressRegion") or "<MISSING>"
    postal = a.get("postalCode") or "<MISSING>"
    g = j.get("geo") or {}
    country_code = g.get("addressCountry") or "<MISSING>"
    store_number = "<MISSING>"
    phone = j.get("telephone") or "<MISSING>"
    latitude = g.get("latitude") or "<MISSING>"
    longitude = g.get("longitude") or "<MISSING>"
    location_type = j.get("@type") or "<MISSING>"

    _tmp = []
    line = "".join(tree.xpath("""//script[contains(text(), '"office":')]/text()"""))
    line = line.split('"office":')[1].split('"access"')[0][:-1]
    try:
        divs = json.loads(line)["hours"]
    except:
        divs = []

    for d in divs:
        day = d.get("day")
        start = d.get("open")
        close = d.get("close")
        if start == close:
            _tmp.append(f"{day}: Closed")
        else:
            _tmp.append(f"{day}: {start} - {close}")

    hours_of_operation = ";".join(_tmp).replace(".5", ":30") or "<MISSING>"

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
