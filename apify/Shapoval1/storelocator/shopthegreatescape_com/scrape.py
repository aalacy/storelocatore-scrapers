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

    r = session.get("https://www.shopthegreatescape.com/store-locator")
    tree = html.fromstring(r.text)

    return tree.xpath("//a[@class='store_link']/@href")


def get_data(url):
    locator_domain = "https://www.shopthegreatescape.com"
    page_url = f"https://www.shopthegreatescape.com{url}"
    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    ad = tree.xpath("//address/text()")
    street_address = "".join(ad[0])
    line = "".join(ad[1])
    city = line.split(",")[0]
    line = line.split(",")[1].strip()
    state = line.split()[0]
    postal = line.split()[1]
    country_code = "US"
    store_number = "<MISSING>"
    location_name = f"The Great Escape - {city}"
    phone = "".join(tree.xpath("//address/following-sibling::p[1]/text()")).strip()
    ll = "".join(tree.xpath('//div[@class="span6"]/iframe/@src'))
    ll = ll.split("!2d")[1].split("!3m")[0].replace("!3d", ",")
    latitude = ll.split(",")[1]
    if latitude.find("!2m") != -1:
        latitude = latitude.split("!2m")[0]
    longitude = ll.split(",")[0]
    location_type = "<MISSING>"
    hours_of_operation = tree.xpath(
        "//h3[contains(text(), 'Store Hours')]/following-sibling::table//tr//text()"
    )
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
