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
    r = session.get("https://www.thecitizensbankphila.com/branches/", headers=headers)
    tree = html.fromstring(r.text)
    return tree.xpath('//a[contains(text(), "BRANCH INFO")]/@href')


def get_data(url):
    locator_domain = "https://www.thecitizensbankphila.com"
    page_url = url
    session = SgRequests()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath('//div[@class="col1"]/h3/text()')) or "<MISSING>"
    if location_name.find("Meridian Broadmoor ATM/ITM") != -1:
        return
    street_address = "".join(
        tree.xpath('//div[@class="col1"]/p[@class="address"]/text()[1]')
    )
    ad = (
        "".join(tree.xpath('//div[@class="col1"]/p[@class="address"]/text()[2]'))
        .replace("\n", "")
        .strip()
    )
    city = ad.split(",")[0].strip()
    state = ad.split(",")[1].split()[0].strip()
    postal = ad.split(",")[1].split()[1].strip()
    country_code = "US"
    store_number = "<MISSING>"
    phone = (
        "".join(tree.xpath('//div[@class="col1"]/p[contains(text(), "Tel")]/text()'))
        .replace("Tel", "")
        .strip()
    )
    location_type = "Branch"
    hours_of_operation = tree.xpath(
        '//div[@class="col2"]/h3/following-sibling::*//text()'
    )
    hours_of_operation = list(filter(None, [a.strip() for a in hours_of_operation]))
    hours_of_operation = " ".join(hours_of_operation)
    if (
        hours_of_operation.find("Lobby") != -1
        and hours_of_operation.find("Drive") != -1
        and hours_of_operation.find("Lobby & Drive") == -1
        and hours_of_operation.find("Lobby and Drive") == -1
    ):
        hours_of_operation = (
            hours_of_operation.split("Lobby")[1].split("Drive")[0].strip()
        )
    if (
        hours_of_operation.find("Lobby & Drive") != -1
        and hours_of_operation.find("ITM") != -1
    ):
        hours_of_operation = (
            hours_of_operation.split("Lobby & Drive Thru")[1].split("ITM")[0].strip()
        )
    if hours_of_operation.find("Drive Thru Only") != -1:
        hours_of_operation = hours_of_operation.split("Drive Thru Only")[1].strip()
    if hours_of_operation.find("Lobby and Drive") != -1:
        hours_of_operation = hours_of_operation.split("Lobby and Drive Thru")[1].strip()
    if hours_of_operation.find("Lobby & Drive Thru") != -1:
        hours_of_operation = hours_of_operation.split("Lobby & Drive Thru")[1].strip()
    hours_of_operation = (
        hours_of_operation.replace("Lobby Only", "").replace("Lobby", "").strip()
    )
    if hours_of_operation.find("Drive Thru") != -1:
        hours_of_operation = hours_of_operation.split("Drive Thru")[0].strip()
    if hours_of_operation.find("ITM") != -1:
        hours_of_operation = hours_of_operation.split("ITM")[0].strip()

    latitude = (
        "".join(tree.xpath('//script[contains(text(), "LatLng")]/text()'))
        .split("LatLng(")[1]
        .split(",")[0]
        .strip()
    )
    longitude = (
        "".join(tree.xpath('//script[contains(text(), "LatLng")]/text()'))
        .split("LatLng(")[1]
        .split(",")[1]
        .split(")")[0]
        .strip()
    )

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
