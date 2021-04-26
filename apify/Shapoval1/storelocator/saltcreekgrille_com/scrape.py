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
    r = session.get("https://saltcreekgrille.com/")
    tree = html.fromstring(r.text)
    return tree.xpath(
        "//ul[@class='sub-menu']/li/a[not(contains(@href, 'menu'))]/@href"
    )


def get_data(url):
    locator_domain = "https://saltcreekgrille.com/"
    page_url = url
    session = SgRequests()

    r = session.get(page_url)
    tree = html.fromstring(r.text)

    line = tree.xpath(
        '//h2[./span[contains(text(), "Address")]]/following-sibling::p[1]/text()'
    )

    street_address = "".join(line[0]).replace("\n", "").strip()
    city = "".join(line[1]).split(",")[0].strip()
    state = "".join(line[1]).split(",")[1].strip().split()[0].strip()
    postal = "".join(line[1]).split(",")[1].strip().split()[1].strip()
    country_code = "US"
    store_number = "<MISSING>"
    location_name = "".join(tree.xpath("//h1/span/text()"))
    phone = "".join(line[2]).replace("\n", "")
    latitude = "".join(
        tree.xpath(
            '//div[@class="column map-container"]/div[@class="marker"]/@data-lat'
        )
    )
    longitude = "".join(
        tree.xpath(
            '//div[@class="column map-container"]/div[@class="marker"]/@data-lng'
        )
    )
    location_type = "<MISSING>"
    hours_of_operation = (
        " ".join(
            tree.xpath(
                '//h2[./span[contains(text(), "Hours")]]/following-sibling::p[1]//text()'
            )
        )
        .replace("\n", "")
        .strip()
    )
    if hours_of_operation.find("Weekend Brunch ") != -1:
        hours_of_operation = hours_of_operation.split("Weekend Brunch ")[0].strip()
    if hours_of_operation.find("*") != -1:
        hours_of_operation = hours_of_operation.split("*")[0].strip()
    if hours_of_operation.find("Sunday Brunch:") != -1:
        hours_of_operation = hours_of_operation.split("Sunday Brunch:")[0].strip()

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
