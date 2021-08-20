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
    r = session.get("https://www.chickenchef.com/locations/")
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[contains(text(), '.addMarker(')]/text()"))
    for t in text.split(".addMarker(")[1:]:
        lat = t.split(",")[0]
        lng = t.split(",")[1]
        url = t.split(",")[2].replace("'", "")
        urls.append((url, (lat, lng)))

    return urls


def get_data(params):
    url = params[0]
    locator_domain = "https://www.chickenchef.com/"
    page_url = f"https://www.chickenchef.com{url}"

    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//h1/@data-title")).strip()
    street_address = (
        "".join(tree.xpath("//p[./strong[text()='Address:']]/text()")).strip()
        or "<MISSING>"
    )
    city = (
        "".join(tree.xpath("//p[./strong[text()='City/Town:']]/text()")).strip()
        or "<MISSING>"
    )
    state = (
        "".join(tree.xpath("//p[./strong[text()='Province:']]/text()")).strip()
        or "<MISSING>"
    )
    postal = (
        "".join(tree.xpath("//p[./strong[text()='Postal Code:']]/text()")).strip()
        or "<MISSING>"
    )
    country_code = "CA"
    store_number = "<MISSING>"
    try:
        phone = tree.xpath("//a[@class='location-telephone']/text()")[0].strip()
    except:
        phone = "<MISSING>"
    latitude, longitude = params[1]
    location_type = "<MISSING>"

    _tmp = []
    days = tree.xpath("//div[@id='restaurant-hours']/p/strong/text()")
    times = tree.xpath("//div[@id='restaurant-hours']/p/text()")

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

    with futures.ThreadPoolExecutor(max_workers=5) as executor:
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
