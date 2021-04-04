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
    r = session.get("https://www.pods.com/sitemap.xml")
    tree = html.fromstring(r.content)
    links = tree.xpath("//loc/text()")
    for link in links:
        if (
            link.find("united-states") != -1 or link.find("canada") != -1
        ) and link.count("/") == 6:
            urls.append(link)

    return urls


def get_data(page_url):
    rows = []
    locator_domain = "https://www.pods.com/"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    text = (
        "".join(
            tree.xpath(
                "//script[contains(text(), 'LocalBusiness') and contains(text(), 'address')]/text()"
            )
        )
        or "{}"
    )

    js = json.loads(text)
    address = js.get("address") or []

    i = 0
    for a in address:
        location_name = (
            "".join(
                tree.xpath(f"//div[@id='warehouse-list-item-{i}']//h3/text()")
            ).strip()
            or "<MISSING>"
        )
        street_address = a.get("streetAddress") or "<MISSING>"
        city = a.get("addressLocality") or "<MISSING>"
        state = a.get("addressRegion") or "<MISSING>"
        postal = a.get("postalCode") or "<MISSING>"
        if len(postal) == 5:
            country_code = "US"
        else:
            country_code = "CA"
        store_number = "<MISSING>"
        phone = js.get("telephone") or "<MISSING>"
        latitude = (
            "".join(tree.xpath(f"//div[@id='warehouse-list-item-{i}']/@data-latitude"))
            or "<MISSING>"
        )
        longitude = (
            "".join(tree.xpath(f"//div[@id='warehouse-list-item-{i}']/@data-longitude"))
            or "<MISSING>"
        )
        if latitude == "0.0" or longitude == "0.0":
            latitude = "<MISSING>"
            longitude = "<MISSING>"

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

        rows.append(row)
        i += 1

    return rows


def fetch_data():
    out = []
    s = set()
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url): url for url in urls}
        for future in futures.as_completed(future_to_url):
            rows = future.result()
            for row in rows:
                _id = tuple(row[2:6])
                if _id not in s:
                    s.add(_id)
                    out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
