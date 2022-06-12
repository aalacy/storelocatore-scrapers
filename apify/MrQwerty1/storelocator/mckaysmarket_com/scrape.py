import csv

from concurrent import futures
from lxml import html
from sgrequests import SgRequests


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
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    r = session.get(
        "https://www2.mckaysmarket.com/StoreLocator/State/?State=OR", headers=headers
    )
    tree = html.fromstring(r.text)

    return tree.xpath("//a[text()='View']/@href")


def get_data(page_url):
    locator_domain = "https://mckaysmarket.com/"

    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    r = session.get(page_url, headers=headers)
    page_url = page_url.split("&")[0]
    tree = html.fromstring(r.text)

    location_name = "".join(
        tree.xpath("//div[@class='row']/following-sibling::h3/text()")
    ).strip()
    line = tree.xpath("//p[@class='Address']/text()")
    line = list(filter(None, [l.strip() for l in line]))

    street_address = line[0]
    line = line[1]
    city = line.split(",")[0].strip()
    line = line.split(",")[1].strip()
    state = line.split()[0]
    postal = line.split()[1]
    country_code = "US"
    store_number = location_name.split("#")[-1].strip()
    phone = (
        "".join(tree.xpath("//p[@class='PhoneNumber']/a/text()")).strip() or "<MISSING>"
    )

    text = "".join(tree.xpath("//script[contains(text(), 'initializeMap(')]/text()"))
    try:
        latitude, longitude = (
            text.split("initializeMap(")[1].split(");")[0].replace('"', "").split(",")
        )
    except IndexError:
        latitude, longitude = "<MISSING>", "<MISSING>"
    location_type = "<MISSING>"

    _tmp = []
    hours = tree.xpath(
        "//dt[text()='Hours of Operation:']/following-sibling::dd[1]/text()"
    )

    for h in hours:
        if not h.strip() or "*" in h:
            continue
        if "Our" in h or "Special" in h:
            break

        _tmp.append(h.replace("Normal Business Hours:", "").strip())

    hours_of_operation = ";".join(_tmp) or "<MISSING>"

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
