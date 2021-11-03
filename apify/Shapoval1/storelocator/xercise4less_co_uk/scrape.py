import csv
from lxml import html
from sgscrape.sgpostal import International_Parser, parse_address
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
        "Referer": "https://www.xercise4less.co.uk/",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
        "TE": "Trailers",
    }
    r = session.get("https://www.xercise4less.co.uk/find-a-gym/", headers=headers)
    tree = html.fromstring(r.content)
    return tree.xpath("//li[@class='gym-locator__gyms-list-item']/a/@href")


def get_data(url):
    locator_domain = "https://www.xercise4less.co.uk"
    page_url = url
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Referer": "https://www.xercise4less.co.uk/",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
        "TE": "Trailers",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.content)
    address = tree.xpath(
        '//div[@class="single-gym-post__details-block-content"]/p/text()/following-sibling::text()'
    )
    address = list(filter(None, [a.strip() for a in address]))
    address = " ".join(address)
    a = parse_address(International_Parser(), address)
    street_address = (
        f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
        or "<MISSING>"
    )
    city = a.city or "<MISSING>"
    postal = a.postcode or "<MISSING>"
    state = a.state or "<MISSING>"
    country_code = "GB"
    page_url = url or "<MISSING>"
    store_number = "<MISSING>"
    location_name = (
        "".join(
            tree.xpath(
                '//div[@class="single-gym-post__details-block-content"]/p/text()[1]'
            )
        ).replace("\n", "")
        or "<MISSING>"
    )
    phone = "".join(tree.xpath('//a[contains(@href, "tel:")]/text()')) or "<MISSING>"
    text = "".join(tree.xpath('//ul/li/a[contains(text(), "view in maps")]/@href'))
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
    hours_of_operation = (
        " ".join(
            tree.xpath(
                './/ul[@class="single-gym-post__details-opening-times"]/li//text()'
            )
        )
        .split("Bank")[0]
        .replace("\n", " ")
        .strip()
        or "Closed"
    )
    if hours_of_operation.find("Temporarily Closed") != -1:
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
