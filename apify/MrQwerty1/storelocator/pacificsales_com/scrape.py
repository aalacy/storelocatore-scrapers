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


def get_ids():
    url = "https://www.bestbuy.com/site/pacific-sales/pacific-sales-store-locator/pcmcat1565294333984.c"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:83.0) Gecko/20100101 Firefox/83.0"
    }
    cookies = {"intl_splash": "false"}

    session = SgRequests()
    r = session.get(url, headers=headers, cookies=cookies)
    tree = html.fromstring(r.text)

    return tree.xpath("//*[@data-store-id]/@data-store-id")


def get_data(_id):
    locator_domain = "https://pacificsales.com/"
    page_url = f"https://stores.bestbuy.com/{_id}"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = tree.xpath("//h1/span[@itemprop='name']/text()")[0].strip()
    street_address = "".join(tree.xpath("//meta[@itemprop='streetAddress']/@content"))
    city = "".join(tree.xpath("//meta[@itemprop='addressLocality']/@content"))
    state = "".join(tree.xpath("//abbr[@itemprop='addressRegion']/text()")).strip()
    postal = "".join(tree.xpath("//span[@itemprop='postalCode']/text()")).strip()
    country_code = "".join(
        tree.xpath("//abbr[@itemprop='addressCountry']/text()")
    ).strip()

    phone = "".join(tree.xpath("//span[@itemprop='telephone']/text()"))
    store_number = _id
    location_type = "<MISSING>"
    latitude = tree.xpath("//meta[@itemprop='latitude']/@content")[0]
    longitude = tree.xpath("//meta[@itemprop='longitude']/@content")[0]

    _tmp = []
    tr = tree.xpath("//tr[contains(@class, 'c-location-hours-details-row')]")
    if len(tr) > 7:
        tr = tr[:7]

    for t in tr:
        day = "".join(t.xpath("./td[1]/text()")).strip()
        time = "".join(
            t.xpath("./td[@class='c-location-hours-details-row-intervals']//text()")
        ).strip()
        _tmp.append(f"{day}: {time}")

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
    ids = get_ids()

    with futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_url = {executor.submit(get_data, _id): _id for _id in ids}
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
