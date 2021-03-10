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
    r = session.get("https://www.tsb.co.uk/branch-locator/sitemap.xml")
    tree = html.fromstring(r.content)

    return tree.xpath("//loc/text()")


def get_data(page_url):
    locator_domain = "https://www.tsb.co.uk/"
    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    text = "".join(
        tree.xpath("//script[contains(text(),'BankOrCreditUnion')]/text()")
    ).strip()

    if not text:
        return
    j = json.loads(text)

    location_name = j.get("name")
    if not location_name:
        return

    a = j.get("address") or {}
    street_address = a.get("streetAddress") or "<MISSING>"
    city = a.get("addressRegion") or "<MISSING>"
    state = a.get("addressLocality") or "<MISSING>"
    postal = a.get("postalCode") or "<MISSING>"
    country_code = "GB"
    store_number = "<MISSING>"
    phone = j.get("telephone") or "<MISSING>"
    latitude = "".join(tree.xpath("//*[@latitude]/@latitude")) or "<MISSING>"
    longitude = "".join(tree.xpath("//*[@longitude]/@longitude")) or "<MISSING>"
    location_type = "<MISSING>"

    _tmp = []
    days = tree.xpath("//dt[@class='day-name']/text()")
    times = tree.xpath("//span[@class='opening-hours-set']/text()")

    for d, t in zip(days, times):
        _tmp.append(f"{d.strip()}: {t.strip()}")

    hours_of_operation = ";".join(_tmp) or "<MISSING>"

    if "".join(times).lower().count("closed") == len(times):
        hours_of_operation = "Closed"

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
                check = tuple(row[2:6])
                if check not in s:
                    s.add(check)
                    out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
