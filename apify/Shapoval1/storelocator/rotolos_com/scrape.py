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
        "Referer": "https://rotolos.com/",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }
    r = session.get("https://rotolos.com/locations/", headers=headers)
    tree = html.fromstring(r.text)

    return tree.xpath("//a[@class='view-details']/@href")


def get_data(url):
    locator_domain = "https://rotolos.com"
    page_url = url

    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Referer": "https://rotolos.com/",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    street_address = "".join(tree.xpath('//div[@class="contact"]/p[1]/text()'))
    ad = "".join(tree.xpath('//div[@class="contact"]/p[2]/text()'))

    city = ad.split(",")[0]
    ad = ad.split(",")[1].strip()
    state = ad.split()[0]
    postal = ad.split()[1]
    country_code = "US"
    store_number = "<MISSING>"
    location_name = (
        "".join(tree.xpath('//h1[@class="entry-title"]/text()'))
        .replace("\n", "")
        .strip()
    )
    phone = "".join(tree.xpath('//div[@class="contact"]/p[3]/text()'))
    latitude = "".join(tree.xpath('//div[@class="acf-map"]/div/@data-lat'))
    longitude = "".join(tree.xpath('//div[@class="acf-map"]/div/@data-lng'))
    location_type = "<MISSING>"
    hours_of_operation = tree.xpath('//div[@class="day"]//text()')
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
