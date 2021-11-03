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
    session = SgRequests()
    r = session.get("https://www.aritzia.com/en/store-locator?view=results")
    tree = html.fromstring(r.text)

    return tree.xpath("//a[contains(@href, '/en/store/')]/@href")


def get_data(url):
    locator_domain = "https://www.aritzia.com/"
    page_url = f"https://www.aritzia.com{url}"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[@type='application/ld+json']/text()"))
    j = json.loads(text)

    location_name = j.get("Name")
    a = j.get("address") or {}
    street_address = (
        a.get("streetAddress").replace("&eacute;", "é").strip() or "<MISSING>"
    )
    city = a.get("addressLocality").replace("&eacute;", "é") or "<MISSING>"
    state = a.get("addressRegion").replace("&eacute;", "é") or "<MISSING>"
    postal = a.get("postalCode") or "<MISSING>"
    if postal.find(" ") == -1:
        country_code = "US"
    else:
        country_code = "CA"

    phone = j.get("telephone") or "<MISSING>"
    text = "".join(
        tree.xpath(
            "//script[contains(text(), 'app.storelocator.initializeMap(')]/text()"
        )
    )
    try:
        text = text.split("app.storelocator.initializeMap(")[1].split(",")
        store_number, latitude, longitude = text[:3]
    except IndexError:
        store_number, latitude, longitude = "<MISSING>", "<MISSING>", "<MISSING>"
    location_type = "<MISSING>"

    _tmp = []
    divs = tree.xpath("//div[contains(@class,'oh-display')]")
    for d in divs:
        day = "".join(d.xpath("./span[@class='oh-display-days']/text()")).strip()
        time = "".join(d.xpath("./span[@class='oh-display-hours']/text()")).strip()
        _tmp.append(f"{day} {time}")

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
