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
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0"
    }
    r = session.get("https://willys.com/locations-sitemap.xml", headers=headers)
    tree = html.fromstring(r.content)
    return tree.xpath("//url/loc/text()")


def get_data(url):
    locator_domain = "https://willys.com/"
    page_url = url
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0"
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.content)
    street_address = (
        "".join(tree.xpath('.//span[@class="segment-street_number"]/text()'))
        + " "
        + "".join(tree.xpath('//span[@class="segment-street_name"]/text()'))
        or "<MISSING>"
    )
    city = "".join(tree.xpath('.//span[@class="segment-city"]/text()')) or "<MISSING>"
    state = (
        "".join(tree.xpath('.//span[@class="segment-state_short"]/text()'))
        or "<MISSING>"
    )
    postal = (
        "".join(tree.xpath('.//span[@class="segment-post_code"]/text()')) or "<MISSING>"
    )
    country_code = "US"
    page_url = url or "<MISSING>"
    store_number = "".join(tree.xpath('.//i[@class="icon-pin"]/text()')) or "<MISSING>"
    location_name = "".join(tree.xpath('.//div[@class="h6"]/text()'))
    phone = "".join(tree.xpath(".//address/a[@href]/text()"))
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    location_type = "<MISSING>"
    hours_of_operation = (
        "".join(tree.xpath('.//div[@class="info-box"]/p/text()'))
        .replace("\n", " ")
        .strip()
        or "<MISSING>"
    )
    if hours_of_operation.find("Temporarily Closed") != -1:
        hours_of_operation = "Closed"
    elif hours_of_operation.find("am") == -1 and hours_of_operation.find("pm") == -1:
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
