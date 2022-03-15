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
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "max-age=0",
    }
    r = session.get("https://www.fbfs.com/landing-page/agent-listing", headers=headers)

    tree = html.fromstring(r.text)
    return tree.xpath('//div[@class="linkContainer"]/a/@href')


def get_data(url):
    locator_domain = "https://fbfs.com/"
    page_url = f"{url}/Locations"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
    }

    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//span[@itemprop="streetAddress"]')

    for d in div:
        location_name = "".join(tree.xpath("//h1/text()")) or "<MISSING>"
        location_type = "<MISSING>"
        street_address = "".join(d.xpath(".//text()")) or "<MISSING>"
        phone = (
            "".join(d.xpath('.//following::a[@itemprop="telephone"][1]/text()'))
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        state = (
            "".join(
                d.xpath(
                    './/following-sibling::span[@itemprop="addressRegion"][1]/text()'
                )
            )
            or "<MISSING>"
        )
        postal = (
            "".join(
                d.xpath('.//following-sibling::span[@itemprop="postalCode"][1]/text()')
            )
            or "<MISSING>"
        )

        country_code = "US"
        city = (
            "".join(
                d.xpath(
                    './/following-sibling::span[@itemprop="addressLocality"][1]/text()'
                )
            )
            or "<MISSING>"
        )
        store_number = "<MISSING>"
        latitude = (
            "".join(
                d.xpath(
                    './/following::div[@class="office-location-map"][1]/@data-latitude'
                )
            )
            or "<MISSING>"
        )
        if latitude == "data-longitude=":
            latitude = "<MISSING>"
        longitude = (
            "".join(
                d.xpath(
                    './/following::div[@class="office-location-map"][1]/@data-longitude'
                )
            )
            or "<MISSING>"
        )
        hours_of_operation = (
            " ".join(
                d.xpath(
                    './/following::li[@itemprop="openingHoursSpecification"][1]/span/text()'
                )
            )
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )

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
    session = SgRequests()
    scrape()
