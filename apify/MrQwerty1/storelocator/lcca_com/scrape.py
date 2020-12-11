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
    session = SgRequests()
    r = session.get("https://lcca.com/locations/")
    tree = html.fromstring(r.text)

    return tree.xpath("//ul[@class='stateList']/li/a/@href")


def get_data(url):
    rows = []
    locator_domain = "https://lcca.com/"
    api_url = f"https://lcca.com{url}"

    session = SgRequests()
    r = session.get(api_url)
    tree = html.fromstring(r.text)
    _div = tree.xpath("//div[@class='col-lg-6 marg-b-30']")

    for d in _div:
        page_url = "".join(d.xpath(".//div[@class='facName']/a/@href")) or "<MISSING>"
        location_name = "".join(d.xpath(".//a/h2/text()")) or "<MISSING>"
        street_address = (
            "".join(d.xpath(".//p[@itemprop='address']/text()"))
            .replace(",", "")
            .strip()
            or "<MISSING>"
        )
        city = (
            "".join(d.xpath(".//span[@itemprop='addressLocality']/text()"))
            or "<MISSING>"
        )
        state = (
            "".join(d.xpath(".//span[@itemprop='addressRegion']/text()")) or "<MISSING>"
        )
        postal = (
            "".join(d.xpath(".//span[@itemprop='postalCode']/text()")) or "<MISSING>"
        )
        country_code = "US"
        store_number = "<MISSING>"
        phone = (
            "".join(d.xpath(".//a[contains(@href,'tel')]/@href")).replace("tel:1-", "")
            or "<MISSING>"
        )
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

    return rows


def fetch_data():
    out = []
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url): url for url in urls}
        for future in futures.as_completed(future_to_url):
            rows = future.result()
            for row in rows:
                out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
