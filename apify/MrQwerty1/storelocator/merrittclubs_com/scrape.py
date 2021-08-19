import csv
import re

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


def get_coords_from_text(text):
    latitude = "".join(re.findall(r"lat:(\d{2}.\d+)", text)).strip() or "<MISSING>"
    longitude = "".join(re.findall(r"lng:(-?\d{2,3}.\d+)", text)).strip() or "<MISSING>"
    return latitude, longitude


def get_urls():
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0"
    }
    r = session.get("https://merrittclubs.com/locations/", headers=headers)
    tree = html.fromstring(r.text)

    return tree.xpath(
        "//a[contains(@class, 'nectar-button') and contains(@href, '/locations/')]/@href"
    )


def get_data(url):
    locator_domain = "https://merrittclubs.com/"
    page_url = f"https://merrittclubs.com{url}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0"
    }

    session = SgRequests()
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//h1/text()")).strip()
    line = tree.xpath("//span[text()='ADDRESS:']/following-sibling::span/text()")
    line = list(filter(None, [l.strip() for l in line]))

    street_address = ", ".join(line[:-1]).strip()
    line = line[-1]
    city = line.split(",")[0].strip()
    line = line.split(",")[1].strip()
    state = line.split()[0]
    postal = line.split()[1]
    country_code = "US"
    store_number = "<MISSING>"
    phone = (
        "".join(
            tree.xpath("//span[text()='PHONE:']/following-sibling::span/text()")
        ).strip()
        or "<MISSING>"
    )

    text = "".join(
        tree.xpath("//script[contains(text(), 'new google.maps.Marker(')]/text()")
    )
    text = text.split("new google.maps.Marker(")[1].split("}")[0]
    latitude, longitude = get_coords_from_text(text)
    location_type = "<MISSING>"
    hours = tree.xpath(
        "//p[./span[text()='STAFFED HOURS:']]/preceding-sibling::p//text()|//span[text()='TEMPORARY HOURS:']/following-sibling::span/text()"
    )
    hours = list(filter(None, [h.strip() for h in hours]))
    hours_of_operation = ";".join(hours) or "<MISSING>"

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
