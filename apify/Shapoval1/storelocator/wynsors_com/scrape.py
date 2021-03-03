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
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }

    r = session.get("https://www.wynsors.com/stores/", headers=headers)
    tree = html.fromstring(r.text)
    return tree.xpath("//a[@class='amlocator-link']/@href")


def get_data(url):
    locator_domain = "https://www.wynsors.com/"
    page_url = url

    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    street_address = (
        "".join(tree.xpath('//span[@class="amlocator-text -bold"]/text()'))
        or "<MISSING>"
    )
    city = "".join(
        tree.xpath('//span[contains(text(), "City")]/following-sibling::span/text()')
    )
    state = "<MISSING>"
    postal = "".join(
        tree.xpath('//span[contains(text(), "Zip:")]/following-sibling::span/text()')
    )
    country_code = "".join(
        tree.xpath(
            '//span[contains(text(), "Country:")]/following-sibling::span/text()'
        )
    )
    page_url = url

    store_number = "<MISSING>"
    location_name = "".join(tree.xpath("//h1/span/text()"))
    phone = "".join(tree.xpath('//a[contains(@href, "tel")]/text()')).replace("\n", "")
    block = (
        r.text.split("locationData: {")[1]
        .split("marker_url:")[0]
        .replace("\n", "")
        .replace("\t", "")
        .strip()
    )
    latitude = block.split("lat:")[1].split(",")[0].strip()
    longitude = block.split("lng:")[1].split(",")[0].strip()
    location_type = "<MISSING>"
    hours = tree.xpath('//div[@class="amlocator-row"]')
    tmp = []
    count = 0
    for h in hours:
        day = "".join(h.xpath('./span[@class="amlocator-cell -day"]/text()'))
        time = "".join(h.xpath('./span[@class="amlocator-cell -time"]/text()'))
        if time == "Closed":
            count += 1
        line = f"{day} - {time}"
        tmp.append(line)

    hours_of_operation = ";".join(tmp) or "<MISSING>"
    if count == 7:
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
