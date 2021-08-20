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
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0"
    }
    r = session.get(
        "https://pizzarev.com/locations-pizza-places-near-me/", headers=headers
    )
    tree = html.fromstring(r.text)

    return tree.xpath("//ul[contains(@class, 'states')]//li/a/@href")


def get_data(page_url):
    locator_domain = "https://pizzarev.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0"
    }

    session = SgRequests()
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//div[@class='loc_name']/a/text()")).strip()
    line = tree.xpath("//div[@class='col-left']/p/text()")
    line = list(filter(None, [l.strip() for l in line]))

    street_address = ", ".join(line[:-1]).strip() or "<MISSING>"
    line = line[-1]
    city = line.split(",")[0].strip()
    state = line.split(",")[1].strip()
    postal = line.split(",")[-1].strip()
    country_code = "US"
    store_number = "<MISSING>"
    phone = (
        "".join(
            tree.xpath("//div[@class='col-left']/p/a[contains(@href, 'tel')]/text()")
        )
        .replace("Phone:", "")
        .strip()
        or "<MISSING>"
    )

    text = "".join(
        tree.xpath("//script[contains(text(),'var pizza_stores = [')]/text()")
    )
    try:
        text = eval(text.split("var pizza_stores = [")[1].split("];")[0])
        latitude = text[0]
        longitude = text[1]
    except IndexError:
        latitude, longitude = "<MISSING>", "<MISSING>"
    location_type = "<MISSING>"

    _tmp = []
    days = tree.xpath("//span[@class='day']/text()")
    times = tree.xpath("//span[@class='time']/text()")

    for d, t in zip(days, times):
        _tmp.append(f"{d.strip()}: {t.strip()}")

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
