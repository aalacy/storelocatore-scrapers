import csv
import json
from lxml import html
from sgrequests import SgRequests
from concurrent import futures


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
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
        "TE": "Trailers",
    }

    r = session.get(
        "https://www.cadence-education.com/cadence-locations-sitemap.xml",
        headers=headers,
    )
    tree = html.fromstring(r.content)

    return tree.xpath("//url/loc/text()")


def get_data(url):
    locator_domain = "https://www.cadence-education.com"
    page_url = url
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
        "TE": "Trailers",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.content)

    street_address = (
        "".join(tree.xpath('//span[@itemprop="streetAddress"]/text()')) or "<MISSING>"
    )
    city = (
        "".join(tree.xpath('//li[@class="address"]/a/text()'))
        .replace("\n", "")
        .strip()
        .replace(",", "")
        or "<MISSING>"
    )

    postal = (
        "".join(tree.xpath('//span[@itemprop="postalCode"]/text()')).replace("\t", "")
        or "<MISSING>"
    )
    state = (
        "".join(tree.xpath('//span[@itemprop="addressRegion"]/text()')) or "<MISSING>"
    )
    country_code = "US"
    store_number = "<MISSING>"
    location_name = "".join(tree.xpath("//h1/text()")).replace("\n", "").strip()
    phone = "".join(tree.xpath('//span[@itemprop="telephone"]/text()')) or "<MISSING>"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    location_type = location_name
    hours_of_operation = tree.xpath('//li[@itemprop="openingHours"]/text()')
    hours_of_operation = list(filter(None, [a.strip() for a in hours_of_operation]))
    hours_of_operation = " ".join(hours_of_operation) or "<MISSING>"
    subr = session.get("https://www.cadence-education.com/locations/", headers=headers)
    block = subr.text.split("var cadence_location_object = ")[1].split(";")[0]
    js = json.loads(block)
    for j in js["locations_data"]:
        subsity = "".join(j.get("post_code"))

        if postal.find(subsity) != -1:
            latitude = j.get("lat")
            longitude = j.get("lng")

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
