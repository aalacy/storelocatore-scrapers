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
    r = session.get("https://www.frostgelato.com/locations/")
    tree = html.fromstring(r.text)
    return set(
        tree.xpath(
            '//div[@class="store-info"]/h3[contains(@data-country, "united")]/a/@href'
        )
    )


def get_data(url):
    locator_domain = "https://www.frostgelato.com"
    page_url = url
    session = SgRequests()

    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath('//h1[@class="entry-title"]/text()'))
    ad = (
        "".join(tree.xpath('//div[@class="location-address"]/text()'))
        .replace("\n", "")
        .replace("Rd,", "Rd")
        .replace("St,", "St")
        .strip()
    )

    location_type = "<MISSING>"
    street_address = " ".join(ad.split(",")[0].split()[:-1])

    phone = "".join(tree.xpath('//div[@class="business-phone phone-c"]/a/text()'))

    state = ad.split(",")[1].split()[0].strip()
    postal = ad.split(",")[1].split()[-1].strip()
    country_code = "US"
    city = ad.split(",")[0].split()[-1].strip()
    store_number = "<MISSING>"

    latitude = (
        "".join(tree.xpath('//script[contains(text(), ".maps.LatLng")]/text()'))
        .split(".maps.LatLng(")[1]
        .split(")")[0]
        .split(",")[0]
        .strip()
    )
    longitude = (
        "".join(tree.xpath('//script[contains(text(), ".maps.LatLng")]/text()'))
        .split(".maps.LatLng(")[1]
        .split(")")[0]
        .split(",")[1]
        .strip()
    )
    hours_of_operation = tree.xpath('//div[@class="hours-operation"]/div//text()')
    hours_of_operation = list(filter(None, [a.strip() for a in hours_of_operation]))
    hours_of_operation = (
        " ".join(hours_of_operation).replace("Hours of Operation:", "").strip()
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
    scrape()
