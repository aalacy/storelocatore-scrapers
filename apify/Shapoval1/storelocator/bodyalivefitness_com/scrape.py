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
        "Referer": "https://bodyalivefitness.com/",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }
    r = session.get("https://bodyalivefitness.com/", headers=headers)
    tree = html.fromstring(r.text)
    return tree.xpath(
        "//li/a[contains(text(), 'Locations')]/following-sibling::ul/li/a/@href | //li/a[contains(text(), 'Locations')]/following-sibling::ul/li/ul/li/a/@href"
    )


def get_data(url):
    locator_domain = "https://bodyalivefitness.com/"
    page_url = "".join(url)
    if page_url.find("cincinnati") != -1:
        return
    session = SgRequests()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Referer": "https://bodyalivefitness.com/",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }

    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    street_address = (
        "".join(tree.xpath('//div[./h4[contains(text(), "(")]]/h4[1]/text()'))
        .replace("\n", "")
        .strip()
    )
    if street_address.find("350") != -1:
        street_address = street_address.split(")")[1]
    ad = (
        "".join(tree.xpath('//div[./h4[contains(text(), "(")]]/h4[2]/text()'))
        .replace("\n", "")
        .strip()
    )
    city = ad.split(",")[0]
    state = ad.split(",")[1].split()[0]
    postal = ad.split(",")[1].split()[-1]
    country_code = "US"
    store_number = "<MISSING>"
    location_name = "".join(tree.xpath("//h2[@style='text-align: center']//text()"))
    phone = (
        "".join(tree.xpath('//div[./h4[contains(text(), "(")]]/h4[3]/text()'))
        .replace("\n", "")
        .strip()
    )
    ll = "".join(tree.xpath('//div[@class="et_pb_code_inner"]/iframe/@src'))
    latitude = ll.split("!3d")[1].strip().split("!")[0].strip()
    longitude = ll.split("!2d")[1].strip().split("!")[0].strip()
    location_type = "<MISSING>"
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
