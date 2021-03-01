import csv
import json
from lxml import html
from sgrequests import SgRequests
from concurrent import futures
from sgscrape.sgpostal import International_Parser, parse_address


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
        "Connection": "keep-alive",
        "Referer": "https://brownssocialhouse.com/",
        "Upgrade-Insecure-Requests": "1",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }
    r = session.get("https://brownssocialhouse.com/#locations-section", headers=headers)
    tree = html.fromstring(r.content)

    return tree.xpath("//a[./strong][not(contains(@href, '#'))]/@href")


def get_data(url):
    locator_domain = "https://brownssocialhouse.com/"
    page_url = "".join(url)
    if page_url.count("/") == 4:
        page_url = (
            " ".join(page_url.split("/")[:-1]).split()[-1].replace("/", "").strip()
        )
    if page_url.count("/") == 3:
        page_url = page_url.split("/")[-1].replace("/", "").strip()
    if page_url.count("/") == 1:
        page_url = page_url.split("/")[-1].replace("/", "").strip()
    page_url = f"https://brownssocialhouse.com/{page_url}"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Referer": "https://brownssocialhouse.com/",
        "Proxy-Authorization": "Basic VEYwYmJlZGNkNWM1YmE1YWZjNDhhOTQ4MjcxMDlmMGJhMS5oNzgzb2hhdzA5amRmMDpURjBiYmVkY2Q1YzViYTVhZmM0OGE5NDgyNzEwOWYwYmExLmg3ODIzOWhk",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    hours_of_operation = (
        " ".join(
            tree.xpath(
                '//h3/strong[contains(text(), "HOURS")]/following::p/text() | //h3/strong[contains(text(), "hOURS")]/following::p/text()'
            )
        )
        .replace("\n", "")
        .strip()
    )
    if hours_of_operation.find("!") != -1:
        hours_of_operation = hours_of_operation.split("!")[1].strip()
    coming_soon = "".join(
        tree.xpath('//div[@class="sqs-block-content"]/h3/strong/text()')
    )
    if coming_soon == "coming soon!" or coming_soon == "coming soon!!":
        hours_of_operation = "Coming Soon!"
    if hours_of_operation.find("Serving") != -1:
        hours_of_operation = hours_of_operation.split("Serving")[0].strip()
    if hours_of_operation.find("We will") != -1:
        hours_of_operation = hours_of_operation.split("We will")[0].strip()
    if hours_of_operation.find("We are") != -1:
        hours_of_operation = hours_of_operation.split("We are")[0].strip()
    js = "".join(
        tree.xpath('//div[@class="sqs-block map-block sqs-block-map"]/@data-block-json')
    )
    j = json.loads(js)
    street_address = "".join(j.get("location").get("addressLine1")).strip()
    ad = "".join(j.get("location").get("addressLine2"))
    a = parse_address(International_Parser(), ad)
    postal = a.postcode or "<MISSING>"
    city = a.city
    state = a.state

    country_code = "".join(j.get("location").get("addressCountry"))

    store_number = "<MISSING>"
    location_name = "".join(j.get("location").get("addressTitle"))

    if page_url.find("portage") != -1:
        postal = tree.xpath('//div[@class="page-description"]/p[1]/text()')
        postal = "".join(postal[0]).split(",")[-1].strip()
    phone = (
        "".join(
            tree.xpath(
                '//div[@class="page-description"]/p[2][contains(text(), "(")]//text() | //div[@class="page-description"]/p[3][contains(text(), "(")]//text() | //div[@class="page-description"]/p/a[contains(text(), "(")]//text() | //div[@class="page-description"]/p[2][contains(text(), "-")]//text()'
            )
        )
        or "<MISSING>"
    )
    if phone.find("BC") != -1:
        phone = phone.split("BC")[1].strip()
    if phone.find("ORDER") != -1:
        phone = phone.split("ORDER")[0].strip()
    latitude = j.get("location").get("mapLat")
    longitude = j.get("location").get("mapLng")
    location_type = "<MISSING>"
    if (
        page_url.find("harvey") != -1
        or page_url.find("qetheatre") != -1
        or page_url.find("st-albert") != -1
        or page_url.find("portage") != -1
    ):
        phone = tree.xpath('//div[@class="page-description"]/p[1]//text()')
        phone = "".join(phone[-1])

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
