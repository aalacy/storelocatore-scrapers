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
    r = session.get("https://www.clarksusa.com/sitemap.xml")
    tree = html.fromstring(r.content)
    sitemap_url = "".join(tree.xpath("//loc[contains(text(),'Store')]/text()"))
    r = session.get(sitemap_url)
    tree = html.fromstring(r.content)

    return tree.xpath("//loc[contains(text(), '/A')]/text()")


def get_data(page_url):
    locator_domain = "https://www.clarksusa.com"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    if page_url != r.url:
        return

    location_name = "".join(tree.xpath("//h1[@itemprop='name']/text()"))
    street_address = " ".join(
        tree.xpath("//input[contains(@id, 'storeAddressLine1')]/@value")
    ).strip()
    city = "".join(tree.xpath("//input[@id='city']/@value")) or "<MISSING>"
    state = "".join(tree.xpath("//input[@id='state']/@value")) or "<MISSING>"
    postal = tree.xpath("//input[@id='postalCode']/@value")[0] or "<MISSING>"
    country_code = "".join(tree.xpath("//input[@id='country']/@value")) or "<MISSING>"
    if country_code == "United States":
        country_code = "US"
    store_number = "".join(tree.xpath("//input[@id='storeId']/@value")) or "<MISSING>"
    phone = "".join(tree.xpath("//p[@itemprop='telephone']/text()")) or "<MISSING>"
    latitude = "".join(tree.xpath("//input[@id='latitude']/@value")) or "<MISSING>"
    longitude = "".join(tree.xpath("//input[@id='longitude']/@value")) or "<MISSING>"

    if location_name.lower().find("outlet") == -1:
        location_type = "Store"
    else:
        location_type = "Outlet"

    _tmp = []
    hours = tree.xpath(
        "//p[@itemprop='openingHours']/following-sibling::p[@class='value']"
    )
    for h in hours:
        day = "".join(h.xpath("./span[1]/text()"))
        time = "".join(h.xpath("./span[2]/text()"))
        _tmp.append(f"{day}: {time}")

    hours_of_operation = ";".join(_tmp) or "<MISSING>"
    if hours_of_operation.count("Closed") == 7:
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
