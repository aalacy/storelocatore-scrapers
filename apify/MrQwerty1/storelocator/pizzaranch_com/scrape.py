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
    for i in range(1, 5000):
        r = session.get(
            f"https://pizzaranch.com/all-locations/search-results/p{i}?state=*"
        )
        tree = html.fromstring(r.text)
        links = tree.xpath("//location-info-panel")
        for l in links:
            lines = l.get(":location", "").split("\n")
            for line in lines:
                if line.find("url:") != -1:
                    u = line.split("'")[1]
                    if u:
                        urls.append(u)
        if len(links) < 12:
            break
    return urls


def get_data(page_url):
    locator_domain = "https://pizzaranch.com"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//h1[@itemprop='name']//text()")).strip()
    street_address = "".join(
        tree.xpath("//span[@itemprop='streetAddress']//text()")
    ).strip()
    city = "".join(tree.xpath("//span[@itemprop='addressLocality']//text()")).strip()
    state = "".join(tree.xpath("//abbr[@itemprop='addressRegion']//text()")).strip()
    postal = "".join(tree.xpath("//span[@itemprop='postalCode']//text()")).strip()
    country_code = "US"
    store_number = "<MISSING>"
    phone = "".join(tree.xpath("//span[@itemprop='telephone']//text()")).strip()
    location_type = "<MISSING>"
    latitude = tree.xpath("//meta[@itemprop='latitude']/@content")[0]
    longitude = tree.xpath("//meta[@itemprop='longitude']/@content")[0]

    _tmp = []

    hours = tree.xpath(
        "//div[@class='location-info-right-wrapper']//table[@class='c-location-hours-details']"
        "//tr[contains(@class, 'c-location-hours-details')]"
    )
    for h in hours:
        day = "".join(h.xpath("./td[@class='c-location-hours-details-row-day']/text()"))
        time = " ".join(
            h.xpath(
                ".//span[@class='c-location-hours-details-row-intervals-instance ']//text()"
            )
        )
        if time:
            _tmp.append(f"{day} {time}")
        else:
            _tmp.append(f"{day} Closed")

    hours_of_operation = ";".join(_tmp) or "<MISSING>"

    if hours_of_operation.count("Closed") == 7:
        hours_of_operation = "Closed"

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
