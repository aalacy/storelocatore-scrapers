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
    }
    r = session.get(
        "https://www.heartland.bank/LEARNING/FAQs/Entries/what-are-your-current-atm-locations",
        headers=headers,
    )
    tree = html.fromstring(r.text)
    return tree.xpath(
        '//h3[text()="What are your current ATM Locations?"]/following-sibling::div//ul/li/a/@href'
    )


def get_data(url):
    locator_domain = "https://www.heartland.bank/"
    page_url = url
    if page_url == "https://www.moneypass.com/index.html":
        return
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
    }
    session = SgRequests()
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    street_address = (
        "".join(tree.xpath('//p[@class="blueAddress"]/text()[1]'))
        .replace("\n", "")
        .strip()
    )
    ad = (
        "".join(tree.xpath('//p[@class="blueAddress"]/text()[2]'))
        .replace("\n", "")
        .strip()
    )
    city = ad.split(",")[0].strip()
    state = ad.split(",")[1].split()[0].strip()
    postal = ad.split(",")[1].split()[1].strip()
    country_code = "US"
    store_number = "<MISSING>"
    location_name = "".join(tree.xpath("//h1/text()"))
    phone = (
        "".join(tree.xpath('//p[contains(text(), "Phone:")]/text()[1]'))
        .replace("Phone:", "")
        .strip()
    )
    latitude = (
        "".join(tree.xpath('//script[contains(text(), "latitude")]/text()'))
        .split('"latitude":')[1]
        .split(",")[0]
        .strip()
    )
    longitude = (
        "".join(tree.xpath('//script[contains(text(), "latitude")]/text()'))
        .split('"longitude":')[1]
        .split("}")[0]
        .strip()
    )
    location_type = "ATM"
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
    with futures.ThreadPoolExecutor(max_workers=1) as executor:
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
