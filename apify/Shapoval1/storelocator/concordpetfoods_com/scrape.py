import csv
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
    r = session.get("https://concordpetfoods.com/pages/locations")
    tree = html.fromstring(r.text)

    return tree.xpath("//a[contains(@href, '/a/pages/locations')]/@href")


def get_data(url):
    locator_domain = "https://concordpetfoods.com"
    page_url = f"https://concordpetfoods.com{url}"
    if url.startswith("https"):
        page_url = url
    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    text = tree.xpath('//div[@class="flex flex-col md:flex-row"]')
    for h in text:

        street_address = (
            "".join(h.xpath('.//span[@itemprop="streetAddress"]/text()')) or "<MISSING>"
        )
        city = (
            "".join(h.xpath('.//span[@itemprop="addressLocality"]/text()'))
            or "<MISSING>"
        )
        state = (
            "".join(h.xpath('.//span[@itemprop="addressRegion"]/text()')) or "<MISSING>"
        )
        postal = (
            "".join(h.xpath('.//span[@itemprop="postalCode"]/text()')) or "<MISSING>"
        )
        country_code = "US"
        page_url = f"https://concordpetfoods.com{url}" or "<MISSING>"
        if url.startswith("https"):
            page_url = url
        store_number = page_url.split("/")[-2]
        location_name = "".join(h.xpath('.//span[@itemprop="name"]/a[@href]/text()'))
        phone = "".join(h.xpath('.//span[@itemprop="telephone"]/a[@href]/text()'))
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        location_type = "<MISSING>"
        hours = h.xpath('.//div[@itemprop="openingHours"]/@content')
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
