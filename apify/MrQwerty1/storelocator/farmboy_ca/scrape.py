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
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
    }
    r = session.get("https://www.farmboy.ca/stores-sitemap.xml", headers=headers)
    tree = html.fromstring(r.content)
    return tree.xpath("//url/loc/text()")


def get_data(page_url):
    locator_domain = "https://www.farmboy.ca/"
    if page_url == "https://www.farmboy.ca/stores/":
        return
    session = SgRequests()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    location_name = "".join(
        tree.xpath('//div[@class="image__header single-store"]/h1/text()')
    )
    ad = (
        "".join(
            tree.xpath('//h2[text()="Store Info"]/following-sibling::div[1]/text()')
        )
        .replace("\n", "")
        .strip()
    )
    street_address = " ".join(ad.split(",")[:-3]).strip()
    csz = " ".join(ad.split(",")[-3:]).strip()

    city = " ".join(csz.split()[:-3]).strip()
    state = " ".join(csz.split()[-3:]).split()[0]
    postal = " ".join(csz.split()[-2:]).strip()
    country_code = "CA"
    store_number = "<MISSING>"
    phone = (
        "".join(tree.xpath('//span[contains(text(), "Phone")]/text()'))
        .replace("Phone:", "")
        .strip()
    )
    location_type = "store"
    hours_of_operation = (
        " ".join(tree.xpath("//ul/li/span/text()")).replace("\n", "").strip()
    )
    latitude = (
        "".join(tree.xpath('//script[contains(text(), "LatLng(")]/text()'))
        .split("LatLng(")[1]
        .split(",")[0]
        .strip()
    )
    longitude = (
        "".join(tree.xpath('//script[contains(text(), "LatLng(")]/text()'))
        .split("LatLng(")[1]
        .split(",")[1]
        .split(")")[0]
        .strip()
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
    scrape()
