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

    r = session.get("https://www.woodranch.com/restaurants/")
    tree = html.fromstring(r.content)
    return tree.xpath("//a[@class='tab']/@href")


def get_data(url):
    locator_domain = "https://www.woodranch.com"
    page_url = f"{locator_domain}{url}"
    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.content)
    street_address = tree.xpath('//span[@itemprop="streetAddress"]/text()')
    if len(street_address) > 1:
        street_address = "".join(street_address[1])
    else:
        street_address = "".join(street_address)
    city = "".join(tree.xpath('//span[@itemprop="addressLocality"]/text()'))
    if city.find("(") != -1:
        city = city.split("(")[0].strip()
    state = "".join(tree.xpath('//span[@itemprop="addressRegion"]/text()'))
    postal = "".join(tree.xpath('//span[@itemprop="postalCode"]/text()'))
    country_code = "US"
    store_number = "<MISSING>"
    location_name = "".join(
        tree.xpath('//h1[@class="reset-margin  no-thumbnail"]/text()')
    )
    phone = "".join(tree.xpath('//p[@itemprop="telephone"]/text()'))
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    location_type = "<MISSING>"
    hours_of_operation = (
        " ".join(
            tree.xpath('//h3/following-sibling::p[contains(text(), "Open")]/text()')
        )
        .replace("/n", "")
        .split("Holidays")[0]
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
