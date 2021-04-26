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
    r = session.get("https://www.mothersmarket.com/locations")
    tree = html.fromstring(r.text)
    return tree.xpath("//div[@class='store-details']/a/@href")


def get_data(url):
    locator_domain = "https://www.mothersmarket.com"
    page_url = f"{locator_domain}{url}"
    session = SgRequests()

    r = session.get(page_url)
    tree = html.fromstring(r.text)

    ad = (
        "".join(
            tree.xpath(
                '//h2[contains(text(), "Address")]/following-sibling::div[1]/text()[2]'
            )
        )
        .replace("\n", "")
        .strip()
    )
    street_address = "".join(
        tree.xpath(
            '//h2[contains(text(), "Address")]/following-sibling::div[1]/text()[1]'
        )
    )
    city = ad.split(",")[0]
    state = ad.split(",")[1].split()[0]
    postal = ad.split(",")[1].split()[1]
    country_code = "US"
    store_number = "<MISSING>"
    location_name = "".join(tree.xpath("//h1/text()"))
    phone = "".join(
        tree.xpath('//h2[contains(text(), "Phone")]/following-sibling::div[1]/a/text()')
    )
    latitude = (
        "".join(tree.xpath('//script[contains(text(), "myLatLng")]/text()'))
        .split("{lat:")[1]
        .split(",")[0]
        .strip()
    )
    longitude = (
        "".join(tree.xpath('//script[contains(text(), "myLatLng")]/text()'))
        .split("lng: ")[1]
        .split("}")[0]
        .strip()
    )
    location_type = "<MISSING>"
    hours_of_operation = (
        " ".join(
            tree.xpath(
                '//h2[contains(text(), "Store Hours")]/following-sibling::div/div//text()'
            )
        )
        .replace("\r", "")
        .replace("\n", "")
        .strip()
    )
    if hours_of_operation.find("December") != -1:
        hours_of_operation = hours_of_operation.split("December")[0].strip()

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
