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
    r = session.get("https://www.tripleos.com/locations/all/")
    tree = html.fromstring(r.text)
    return tree.xpath('//ul[@class="location-list"]/li/a/@href')


def get_data(url):
    locator_domain = "https://www.tripleos.com"
    page_url = "".join(url)
    session = SgRequests()

    r = session.get(page_url)
    tree = html.fromstring(r.text)
    line = "".join(tree.xpath('//a[@class="location__address"]/text()'))
    street_address = line.split(",")[0]
    city = line.split(",")[1].strip()
    state = "<MISSING>"
    postal = line.split(",")[-1].strip()
    country_code = "CA"
    store_number = "<MISSING>"
    location_name = "".join(tree.xpath('//h1[@class="location__title"]/text()'))
    phone = "".join(tree.xpath('//div[@class="location__phone"]/a/text()')).strip()
    if phone.find("ext") != -1:
        phone = phone.split("ext")[0].strip()
    latitude = "".join(tree.xpath('//div[@class="marker"]/@data-lat')) or "<MISSING>"
    longitude = "".join(tree.xpath('//div[@class="marker"]/@data-lng')) or "<MISSING>"
    location_type = "<MISSING>"
    hours_of_operation = tree.xpath('//table[@class="location__hours"]/tr/td/text()')
    hours_of_operation = list(filter(None, [a.strip() for a in hours_of_operation]))
    hours_of_operation = " ".join(hours_of_operation) or "<MISSING>"
    notice = "".join(tree.xpath('//div[@class="location__special-notice"]/p/text()'))
    if notice.find("Closed temporarily") != -1:
        hours_of_operation = "Closed temporarily"
    if notice.find("Opening") != -1:
        hours_of_operation = "Coming Soon"

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
    with futures.ThreadPoolExecutor(max_workers=5) as executor:
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
