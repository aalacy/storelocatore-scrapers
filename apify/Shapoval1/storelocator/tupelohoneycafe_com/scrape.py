import csv
from lxml import html
from concurrent import futures
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

    r = session.get("https://tupelohoneycafe.com/locations/")

    tree = html.fromstring(r.content)

    return tree.xpath("//div[@class='main_menu_locations_aligner']/ul/li/ul/li/a/@href")


def get_data(url):
    locator_domain = "https://tupelohoneycafe.com"
    page_url = f"https://tupelohoneycafe.com{url}"
    session = SgRequests()
    r = session.get(page_url)

    tree = html.fromstring(r.text)

    street_address = " ".join(
        tree.xpath('//a[@itemprop="address"]/span[@itemprop="streetAddress"]/text()')
    )
    city = " ".join(
        tree.xpath('//a[@itemprop="address"]/span[@itemprop="addressLocality"]/text()')
    )
    postal = "".join(
        tree.xpath('//a[@itemprop="address"]/span[@itemprop="postalCode"]/text()')
    )
    state = "".join(
        tree.xpath('//a[@itemprop="address"]/span[@itemprop="addressRegion"]/text()')
    )
    country_code = "US"
    store_number = "<MISSING>"
    location_name = "".join(tree.xpath("//h1/text()"))
    phone = "".join(
        tree.xpath(
            '//h3[contains(text(), "Address")]/following-sibling::p[1]/span/text()'
        )
    )
    text = "".join(tree.xpath('//a[@itemprop="address"]/@href'))

    try:
        if text.find("ll=") != -1:
            latitude = text.split("ll=")[1].split(",")[0]
            longitude = text.split("ll=")[1].split(",")[1].split("&")[0]
        else:
            latitude = text.split("@")[1].split(",")[0]
            longitude = text.split("@")[1].split(",")[1]
    except IndexError:
        latitude, longitude = "<MISSING>", "<MISSING>"
    location_type = "<MISSING>"
    hours_of_operation = (
        " ".join(tree.xpath('//div[@itemprop="openingHoursSpecification"]/p[1]/text()'))
        .replace("\n", "")
        .strip()
    )
    coming_soon = "".join(tree.xpath('//div[@class="promotion-title-block"]/h3/text()'))
    if coming_soon.find("Coming") != -1:
        location_name = "<MISSING>"
        street_address = "<MISSING>"
        city = "<MISSING>"
        state = "<MISSING>"
        postal = "<MISSING>"
        phone = "<MISSING>"
        hours_of_operation = "Coming Soon"
    if city.find("Denver") != -1:
        hours_of_operation = (
            " ".join(
                tree.xpath('//div[@itemprop="openingHoursSpecification"]/p[2]/text()')
            )
            .replace("\n", "")
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
