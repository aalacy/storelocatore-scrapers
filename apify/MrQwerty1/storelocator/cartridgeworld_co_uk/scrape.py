import csv

from concurrent import futures
from lxml import html
from sgrequests import SgRequests
from sgscrape.sgpostal import parse_address, International_Parser


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
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0"
    }
    r = session.get("https://www.cartridgeworld.co.uk/locations", headers=headers)
    tree = html.fromstring(r.text)

    return tree.xpath("//a[@class='view-detail']/@href")


def get_data(page_url):
    locator_domain = "https://www.cartridgeworld.co.uk/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0"
    }

    session = SgRequests()
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//div[@class='store-info']/h4/text()")).strip()
    line = "".join(
        tree.xpath("//div[@class='store-info']/p[@class='address-store']/text()")
    ).strip()
    adr = parse_address(International_Parser(), line)
    street_address = (
        f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
            "None", ""
        ).strip()
        or "<MISSING>"
    )
    if (
        street_address.lower().find("online") != -1
        or street_address.lower().find("closed") != -1
    ):
        street_address = "<MISSING>"

    city = adr.city or "<MISSING>"
    state = adr.state or "<MISSING>"
    postal = adr.postcode or "<MISSING>"
    country_code = "GB"
    store_number = "<MISSING>"
    text = tree.xpath("//div[@class='store-info']//text()")
    phone = text[text.index("Phone no:") + 1]
    script = "".join(tree.xpath("//script[contains(text(), 'var markers1 = ')]/text()"))
    latitude = script.split("lat:")[1].split(",")[0]
    longitude = script.split("lng:")[1].split(",")[0]
    location_type = "<MISSING>"

    _tmp = []
    tr = tree.xpath("//table[@class='table']//tr")
    for t in tr:
        day = "".join(t.xpath("./td[1]/text()")).strip()
        time = "".join(t.xpath("./td[2]/text()")).strip()
        _tmp.append(f"{day} {time}")

    hours_of_operation = ";".join(_tmp) or "<MISSING>"

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
