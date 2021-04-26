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

    r = session.get("https://www.morganjewelers.com/")
    tree = html.fromstring(r.text)
    return tree.xpath(
        "//div[@class='top-i-banner-content']/span/p/following-sibling::p/a[not(contains(@href, '/warranties'))]/@href"
    )


def get_data(url):
    locator_domain = "https://www.morganjewelers.com"
    page_url = f"https://www.morganjewelers.com{url}"

    session = SgRequests()

    r = session.get(page_url)
    tree = html.fromstring(r.text)
    line = "".join(
        tree.xpath('//div[@class="contact_us target-subject-row"]/p[2]/text()')
    )
    street_address = "".join(
        tree.xpath('//div[@class="contact_us target-subject-row"]/p[1]/text()')
    )
    city = line.split(",")[0]
    line = line.split(",")[1].strip()
    state = line.split()[0]
    postal = line.split()[1]
    country_code = "US"
    store_number = "<MISSING>"
    location_name = "".join(
        tree.xpath('//div[@class="heading_line store-head"]/h1/text()')
    ).capitalize()
    phone = "".join(
        tree.xpath('//div[@class="store_ctas1"]/p/a[contains(@href, "tel")]/text()')
    )
    text = "".join(tree.xpath('//a[@class="store_links1"]/@href'))
    try:
        if text.find("ll=") != -1:
            latitude = text.split("ll=")[1].split(",")[0]
            longitude = text.split("ll=")[1].split(",")[1].split("&")[0]
        else:
            latitude = text.split("@")[1].split(",")[0]
            longitude = text.split("@")[1].split(",")[1]
    except IndexError:
        latitude, longitude = "<MISSING>", "<MISSING>"
    location_type = "<MISSING>"
    hours_of_operation = tree.xpath('//p[@class="store-hour-container"]/text()')
    hours_of_operation = list(filter(None, [a.strip() for a in hours_of_operation]))
    hours_of_operation = " ".join(hours_of_operation)

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
