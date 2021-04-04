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
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0"
    }
    session = SgRequests()
    r = session.get("https://thelostcajun.com/locations", headers=headers)
    tree = html.fromstring(r.text)

    return tree.xpath(
        "//div[@class='views-field views-field-title']/span/a[./sup]/@href"
    )


def get_data(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0"
    }
    locator_domain = "https://thelostcajun.com/"
    page_url = f"https://thelostcajun.com{url}"

    session = SgRequests()
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[contains(text(),'jQuery.extend')]/text()"))
    text = text.split('"markers":[')[1].split("]")[0]
    js = json.loads(text)

    location_name = "".join(tree.xpath("//title/text()")).split("|")[0].strip()
    source = js.get("text")
    root = html.fromstring(source)
    street_address = (
        " ".join(
            ", ".join(root.xpath("//span[@itemprop='streetAddress']/text()")).split()
        )
        or "<MISSING>"
    )
    city = (
        "".join(root.xpath("//span[@itemprop='addressLocality']/text()")).strip()
        or "<MISSING>"
    )
    state = (
        "".join(root.xpath("//span[@itemprop='addressRegion']/text()")).strip()
        or "<MISSING>"
    )
    postal = (
        "".join(root.xpath("//span[@itemprop='postalCode']/text()")).strip()
        or "<MISSING>"
    )
    country_code = "US"
    store_number = "<MISSING>"
    phone = (
        "".join(root.xpath("//span[@itemprop='telephone']/text()")).strip()
        or "<MISSING>"
    )
    latitude = (
        "".join(root.xpath("//abbr[@class='latitude']/@title")).strip() or "<MISSING>"
    )
    longitude = (
        "".join(root.xpath("//abbr[@class='longitude']/@title")).strip() or "<MISSING>"
    )
    location_type = "<MISSING>"

    _tmp = []
    days = tree.xpath("//span[@class='oh-display-label']/text()")
    times = tree.xpath("//span[@class='oh-display-times oh-display-hours']/text()")

    for d, t in zip(days, times):
        _tmp.append(f"{d.strip()} {t.strip()}")

    hours_of_operation = ";".join(_tmp) or "<MISSING>"
    if phone == "<MISSING>":
        hours_of_operation = "Coming Soon"

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
