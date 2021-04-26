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
        "Proxy-Authorization": "Basic YWNjZXNzX3Rva2VuOmc3NzExNnBzajZqbGZhaHM5dHJwMDdocm0ydTlxNGVzM3BhaGNrYm9oY2kzOGEzMWtpdQ==",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
        "TE": "Trailers",
    }
    r = session.get("https://www.petclubstores.com/", headers=headers)
    tree = html.fromstring(r.text)
    return tree.xpath(
        "//ul[@class='cf']/li/div/a[contains(text(), 'Locations')]/following-sibling::div/ul[@class='folder-child']/li/a/@href"
    )


def get_data(url):
    locator_domain = "https://www.petclubstores.com"
    page_url = f"{locator_domain}{url}"
    if page_url.find("locations-1") != -1:
        return
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Proxy-Authorization": "Basic YWNjZXNzX3Rva2VuOmc3NzExNnBzajZqbGZhaHM5dHJwMDdocm0ydTlxNGVzM3BhaGNrYm9oY2kzOGEzMWtpdQ==",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
        "TE": "Trailers",
    }

    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    line = "".join(
        tree.xpath(
            "//h2[contains(text(), 'Address')]/following-sibling::p[1]/text()[2]"
        )
    )
    street_address = "".join(
        tree.xpath(
            "//h2[contains(text(), 'Address')]/following-sibling::p[1]/text()[1]"
        )
    )
    city = line.split(",")[0]
    state = line.split(",")[1].split()[0]
    postal = line.split(",")[1].split()[1]
    country_code = "US"
    store_number = "<MISSING>"
    hours_of_operation = " ".join(
        tree.xpath("//h2[contains(text(), 'Hours')]/following-sibling::p[1]/text()")
    )
    location_name = (
        " ".join(tree.xpath('//div[@class="sqs-block-content"]/h1/text()'))
        .replace("\n", "")
        .strip()
    )
    phone = (
        "".join(
            tree.xpath(
                "//h2[contains(text(), 'Contact')]/following-sibling::p[1]/text()[1]"
            )
        )
        .replace("Phone:", "")
        .replace("Ph:", "")
        .strip()
    )
    location_type = "<MISSING>"
    ll = "".join(
        tree.xpath(
            '//div[contains(@class, "sqs-block map-block sqs-block-map")]/@data-block-json'
        )
    )
    js = json.loads(ll)
    for j in js.values():
        latitude = j.get("mapLat")
        longitude = j.get("mapLng")

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
