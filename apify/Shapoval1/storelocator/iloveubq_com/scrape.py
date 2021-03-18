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
    r = session.get("https://www.urbanbarbq.com/Locations.aspx")
    tree = html.fromstring(r.text)

    return tree.xpath('//a[@class="lnkStoreName"]/@href')


def get_data(url):
    locator_domain = "https://iloveubq.com"
    page_url = f"https://www.urbanbarbq.com{url}"
    session = SgRequests()
    r = session.get(page_url)


    tree = html.fromstring(r.text)

    hours_of_operation = "<MISSING>"
    country_code = "US"
    line = "".join(tree.xpath('//div[@class="store-address-line2"]/text()')).replace(
        "-", " "
    )
    street_address = "".join(tree.xpath('//div[@class="store-address-line1"]/text()'))
    postal = line.split()[2]
    city = line.split()[0]
    state = line.split()[1]
    store_number = "<MISSING>"
    location_name = "".join(tree.xpath('//div[@class="store-name"]/span/text()'))
    phone = "".join(tree.xpath('//span[@class="store-phone"]/text()'))
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    location_type = "<MISSING>"

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
