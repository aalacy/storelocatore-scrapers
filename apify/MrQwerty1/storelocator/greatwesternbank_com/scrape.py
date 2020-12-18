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
    urls = []
    session = SgRequests()
    r = session.get("https://www.greatwesternbank.com/sitemap.xml")
    tree = html.fromstring(r.content)
    links = tree.xpath("//loc[contains(text(), '/locations/')]/text()")
    for link in links:
        if link.count("/") > 5:
            urls.append(link)

    return urls


def get_data(page_url):
    locator_domain = "https://www.greatwesternbank.com/"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    location_name = (
        "".join(tree.xpath("//h1[@itemprop='name']/text()")).strip() or "<MISSING>"
    )
    if location_name == "<MISSING>":
        return
    street_address = (
        " ".join(
            "".join(tree.xpath("//span[@itemprop='streetAddress']/text()")).split()
        ).strip()
        or "<MISSING>"
    )
    city = (
        "".join(tree.xpath("//span[@itemprop='addressLocality']/text()")).strip()
        or "<MISSING>"
    )
    state = (
        "".join(tree.xpath("//span[@itemprop='addressRegion']/text()")).strip()
        or "<MISSING>"
    )
    postal = (
        "".join(tree.xpath("//span[@itemprop='postalCode']/text()")).strip()
        or "<MISSING>"
    )
    country_code = "US"
    store_number = "<MISSING>"
    phone = (
        "".join(tree.xpath("//span[@itemprop='telephone']/text()")).strip()
        or "<MISSING>"
    )

    try:
        line = "".join(
            tree.xpath("//a[contains(@href, 'http://maps.google.com/maps?q=')]/@href")
        )
        line = "(" + line.split("http://maps.google.com/maps?q=")[1] + ")"
        latitude, longitude = eval(line)
    except IndexError:
        latitude = "<MISSING>"
        longitude = "<MISSING>"

    location_type = "<MISSING>"

    _tmp = []
    ul = tree.xpath("//ul[@class='hours-list']")
    if ul:
        li = ul[0].xpath(".//li")
        for l in li:
            day = "".join(
                l.xpath("./span[@class='hours-list__item__day']/text()")
            ).strip()
            time = "".join(
                l.xpath("./span[@class='hours-list__item__time']//text()")
            ).strip()
            _tmp.append(f"{day}: {time}")

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
