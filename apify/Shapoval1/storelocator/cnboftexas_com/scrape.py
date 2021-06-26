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
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
    }
    r = session.get("https://www.cnboftexas.com/locations/", headers=headers)
    tree = html.fromstring(r.text)
    return tree.xpath('//a[text()="View Details"]/@href')


def get_data(url):
    locator_domain = "https://www.cnboftexas.com/"
    page_url = f"https://www.cnboftexas.com/locations/{url}"
    session = SgRequests()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    location_name = "".join(
        tree.xpath('//h1[@class="blue"]/text() | //h3[@class="blue"]/text()')
    )
    street_address = (
        "".join(tree.xpath('//div[./p[@class="phone"]]/p[2]/text()[1]'))
        .replace("\n", "")
        .strip()
    )
    ad = (
        "".join(tree.xpath('//div[./p[@class="phone"]]/p[2]/text()[2]'))
        .replace("Stephenville", "Stephenville,")
        .replace("\n", "")
        .strip()
    )
    city = ad.split(",")[0].strip()
    state = ad.split(",")[1].split()[0].strip()
    postal = ad.split(",")[1].split()[1].strip()
    country_code = "US"
    store_number = "<MISSING>"
    phone = "".join(tree.xpath('//p[@class="phone"]//text()')).replace("\n", "").strip()
    location_type = "Branch"
    hours_of_operation = tree.xpath(
        '//strong[text()="Lobby Hours "]/following-sibling::text()'
    )
    hours_of_operation = list(filter(None, [a.strip() for a in hours_of_operation]))
    hours_of_operation = (
        " ".join(hours_of_operation).replace("Closed for Lunch 12 - 1", "").strip()
    )
    latitude = (
        "".join(tree.xpath('//script[contains(text(), "Latitude")]/text()'))
        .split("Latitude =")[1]
        .split(";")[0]
        .strip()
    )
    longitude = (
        "".join(tree.xpath('//script[contains(text(), "Latitude")]/text()'))
        .split("Longitude =")[1]
        .split(";")[0]
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
