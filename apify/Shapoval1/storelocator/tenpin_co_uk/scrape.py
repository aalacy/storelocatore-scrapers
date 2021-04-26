import csv
from sgscrape.sgpostal import International_Parser, parse_address
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

    r = session.get("https://www.tenpin.co.uk/our-locations/")
    tree = html.fromstring(r.text)

    return tree.xpath("//a[@class='c-button c-button--locations']/@href")


def get_data(url):
    locator_domain = "https://www.tenpin.co.uk"
    page_url = f"https://www.tenpin.co.uk{url}"
    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    line = " ".join(
        tree.xpath(
            '//div[@class="c-content-block__content c-content-block__content--padding-left"]/p/text()'
        )
    ).replace("\xa0", "")
    a = parse_address(International_Parser(), line)
    street_address = f"{a.street_address_1} {a.street_address_2}".replace(
        "None", ""
    ).strip()
    city = a.city or "<MISSING>"
    state = "<MISSING>"
    postal = a.postcode or "<MISSING>"
    if street_address.find("Xscape") != -1:
        street_address = "".join(line.split(",")[0:3]).strip()
        city = "".join(line.split(",")[3]).strip()
        postal = "".join(line.split(",")[-1]).strip()
    if street_address.find("Albion") != -1:
        street_address = "".join(line.split(",")[0]).strip()
        city = "".join(line.split(",")[1]).strip()
        postal = "".join(line.split(",")[-1]).strip()
    if street_address.find("Braehead") != -1:
        postal = "".join(line.split(",")[-1]).strip()
        street_address = "".join(line.split(",")[:-1]).strip()
    country_code = "GB"
    store_number = "<MISSING>"
    location_name = " ".join(
        tree.xpath('//span[@class="c-hero__title-underline"]/text()')
    )
    phone = "<MISSING>"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    location_type = "<MISSING>"
    hours_of_operation = "<MISSING>"
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
