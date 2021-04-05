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
    r = session.get(
        "https://www.topsmarkets.com/StoreLocator/Search/?ZipCode=75022&miles=10000"
    )
    tree = html.fromstring(r.text)

    return tree.xpath("//div[@id='StoreLocator']//td/a/@href")


def get_data(url):
    locator_domain = "https://www.topsmarkets.com/"
    page_url = url.split("&")[0]

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = (
        "".join(tree.xpath("//div[@class='row']//h3/text()")).strip() or "<MISSING>"
    )
    line = tree.xpath("//p[@class='Address']/text()")
    line = list(filter(None, [l.strip() for l in line]))
    street_address = line[0]
    line = line[-1]
    city = line.split(",")[0].strip()
    line = line.split(",")[-1].strip()
    state = line.split()[0].strip()
    postal = line.split()[1].strip()
    country_code = "US"
    store_number = (
        "".join(tree.xpath("//p[@class='StoreNumber']/text()")).strip() or "<MISSING>"
    )
    phone = tree.xpath("//p[@class='PhoneNumber']/a/text()")[0].strip() or "<MISSING>"
    try:
        script = "".join(
            tree.xpath("//script[contains(text(), 'initializeMap')]/text()")
        ).split("initializeMap")[1]
        latitude, longitude = eval(script.split(";")[0])
    except:
        latitude = "<MISSING>"
        longitude = "<MISSING>"
    location_type = "<MISSING>"
    try:
        hours_of_operation = tree.xpath(
            "//dl[./dt[contains(text(), 'Hours of Operation:')]]/dd/text()"
        )[0]
    except IndexError:
        hours_of_operation = "<MISSING>"

    if hours_of_operation == "Mon - Sun: Closed":
        return

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
