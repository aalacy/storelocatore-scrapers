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
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Referer": "https://lawtons.ca/",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
        "TE": "Trailers",
    }
    r = session.get("https://lawtons.ca/sitemaps/store-sitemap1.xml", headers=headers)
    tree = html.fromstring(r.content)

    return tree.xpath("//lastmod//preceding-sibling::loc[1]/text()")


def get_data(url):
    locator_domain = "https://lawtons.ca"

    page_url = url
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Referer": "https://lawtons.ca/",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
        "TE": "Trailers",
    }
    r = session.get(page_url, headers=headers)

    tree = html.fromstring(r.text)
    hours = tree.xpath('//table[@class="holiday_hours_tbl"]/tbody/tr')
    tmp = []
    for h in hours:
        day = "".join(h.xpath("./td[1]/text()"))
        time = "".join(h.xpath("./td[2]/text()"))
        if time == "":
            time = "Closed"
        line = f"{day} - {time}"
        tmp.append(line)
    hours_of_operation = ";".join(tmp) or "<MISSING>"
    if hours_of_operation.count("Closed") == 7:
        hours_of_operation = "Closed"
    street_address = "".join(
        tree.xpath('//span[@class="location_address_address_1"]/text()')
    )

    city = "".join(tree.xpath('//span[@class="city"]/text()'))
    state = "".join(tree.xpath('//span[@class="province"]/text()'))
    postal = "".join(tree.xpath('//span[@class="postal_code"]/text()')) or "<MISSING>"
    country_code = "CA"
    store_number = "<MISSING>"
    location_name = "".join(tree.xpath('//h2[@class="fl-heading"]/span/text()'))

    phone = (
        "".join(tree.xpath('//div[@class="single_store_info contact"]//a/text()'))
        or "<MISSING>"
    )
    latitude = "".join(
        tree.xpath('//div[@class="fl-module-content fl-node-content"]/div/@data-lat')
    )
    longitude = "".join(
        tree.xpath('//div[@class="fl-module-content fl-node-content"]/div/@data-lng')
    )
    location_type = "<MISSING>"
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
