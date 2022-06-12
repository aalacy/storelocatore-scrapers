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
    }
    r = session.get("https://riverbankandtrust.com/about-us/locations", headers=headers)
    tree = html.fromstring(r.text)
    return tree.xpath('//a[@class="stretched-link"]/@href')


def get_data(url):
    locator_domain = "https://riverbankandtrust.com"
    page_url = url
    session = SgRequests()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//h2/text()"))
    street_address = (
        "".join(tree.xpath('//a[contains(@href, "goo.gl")]/text()[1]'))
        .replace("\n", "")
        .strip()
        or "<MISSING>"
    )
    ad = (
        "".join(tree.xpath('//a[contains(@href, "goo.gl")]/text()[2]'))
        .replace("\n", "")
        .strip()
        or "<MISSING>"
    )
    city = "<MISSING>"
    state = "<MISSING>"
    postal = "<MISSING>"
    country_code = "US"
    if ad != "<MISSING>":
        city = ad.split(",")[0].strip()
        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[1].strip()
    store_number = "<MISSING>"
    phone = "".join(tree.xpath('//em[text()="Office"]/following-sibling::a[1]//text()'))
    location_type = "<MISSING>"
    hours_of_operation = (
        " ".join(tree.xpath('//h3[text()="Hours"]/following-sibling::p[1]//text()'))
        .replace("\n", "")
        .strip()
        or "<MISSING>"
    )
    if (
        hours_of_operation.find("Drive") != -1
        and hours_of_operation.find("Lobby") != -1
    ):
        hours_of_operation = hours_of_operation.split("Drive")[0].strip()
    hours_of_operation = (
        hours_of_operation.replace("Lobby", "").replace("Drive Thru", "").strip()
    )
    latitude = "<MISSING>"
    longitude = "<MISSING>"

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
