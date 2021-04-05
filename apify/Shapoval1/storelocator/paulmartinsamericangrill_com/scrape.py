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
    r = session.get("https://paulmartinsamericangrill.com/locations/")
    tree = html.fromstring(r.text)
    return tree.xpath('//div[@class="tile one col-sm-6 col-md-4"]/a/@href')


def get_data(url):
    locator_domain = "https://paulmartinsamericangrill.com"
    page_url = url
    session = SgRequests()

    r = session.get(page_url)
    tree = html.fromstring(r.text)
    street_address = "".join(tree.xpath('//p[@itemprop="streetAddress"]/text()'))
    city = "".join(tree.xpath('//span[@itemprop="addressLocality"]/text()'))
    state = "".join(tree.xpath('//span[@itemprop="addressRegion"]/text()'))
    postal = "".join(tree.xpath('//span[@itemprop="postalCode"]/text()'))
    country_code = "US"
    store_number = "<MISSING>"
    location_name = "".join(
        tree.xpath('//h1[@class="topbottom-line entry-title"]//text()')
    )
    phone = "".join(tree.xpath('//p[@itemprop="telephone"]/text()'))
    ll = (
        "".join(tree.xpath('//script[contains(text(), "LatLng")]/text()'))
        .split("center: new google.maps.LatLng(")[1]
        .split(")")[0]
    )
    latitude = ll.split(",")[0]
    longitude = ll.split(",")[1]
    location_type = "<MISSING>"
    hours_of_operation = " ".join(
        tree.xpath("//h4[contains(text(), 'Location')]/following-sibling::p[2]/text()")
    ).replace("\n", "")

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
