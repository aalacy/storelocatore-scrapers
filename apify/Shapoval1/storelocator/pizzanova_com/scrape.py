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
        "Connection": "keep-alive",
        "Referer": "https://pizzanova.com/",
        "Upgrade-Insecure-Requests": "1",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }

    r = session.get("https://pizzanova.com/store-locations/", headers=headers)

    tree = html.fromstring(r.text)

    return tree.xpath('//div[@class="sub-city-section"]/a/@href')


def get_data(url):
    locator_domain = "https://pizzanova.com"
    page_url = f"https://pizzanova.com/{url}"
    if page_url.find("com//") != -1:
        page_url = page_url.replace("com//", "com/")
    if page_url.find("belleville-94") != -1:
        return
    if page_url.find("etobicoke-1701") != -1:
        return

    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Connection": "keep-alive",
        "Referer": "https://pizzanova.com/",
        "Upgrade-Insecure-Requests": "1",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }

    r = session.get(page_url, headers=headers)

    tree = html.fromstring(r.text)

    line = "".join(
        tree.xpath("//strong[contains(text(), 'ADDRESS')]/following-sibling::text()[1]")
    )
    street_address = "".join(line.split(",")[0]).strip()
    city = "".join(line.split(",")[1]).strip()
    line = line.split(",")[2]
    state = line.split()[0]
    postal = " ".join(line.split()[-2:])
    if line.count(" ") == 2:
        postal = line.split()[-1]
    country_code = "Canada"
    store_number = "<MISSING>"
    location_name = "".join(tree.xpath('//h1[@class="page-title"]/text()'))
    phone = "".join(
        tree.xpath("//strong[contains(text(), 'PHONE')]/following-sibling::text()")
    ).strip()
    hours_of_operation = (
        " ".join(
            tree.xpath("//strong[contains(text(), 'HOURS')]/following-sibling::text()")
        )
        .replace("\n", "")
        .strip()
        or " ".join(
            tree.xpath(
                "//p[.//strong[contains(text(), 'HOLIDAY')]]/preceding-sibling::p[contains(text(), 'am')]/text()"
            )
        )
        .replace("\n", "")
        .strip()
    )
    if (
        page_url.find("hamilton-1016") != -1
        or page_url.find("hamilton-1160") != -1
        or page_url.find("hamilton-700") != -1
        or page_url.find("hamilton-1405") != -1
    ):
        hours_of_operation = (
            "".join(tree.xpath('//div[@class="schema-code"]/p/script/text()'))
            .split('"openingHours": [')[1]
            .split('"],')[0]
            .replace('"', "")
            .strip()
        )
    ll = "".join(tree.xpath('//div[@class="main-flex-1"]//iframe/@src')) or "<MISSING>"
    ll = ll.split("!2d")[1].split("!3m")[0].replace("!3d", ",") or ll.split("!2d")[
        1
    ].split("!2m")[0].replace("!3d", ",")
    if ll.find("!2m") != -1:
        ll = ll.split("!2m")[0]
    latitude = "".join(ll.split(",")[1]).strip()
    longitude = "".join(ll.split(",")[0]).strip()

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
    with futures.ThreadPoolExecutor(max_workers=5) as executor:
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
