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


def get_friendswood():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0"
    }

    session = SgRequests()
    locator_domain = "https://perryssteakhouse.com/"
    page_url = "https://perryandsonsmarketandgrille.com/locations_category/friendswood"
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    location_name = "".join(
        tree.xpath("//div[@class='col-md-4 col-sm-5']/h3/text()")
    ).strip()
    line = tree.xpath("//div[@class='taxonomy-description']/p[4]/text()")
    line = list(filter(None, [l.strip() for l in line]))
    street_address = line[0]
    phone = line[-1]
    line = line[1]
    city = line.split(",")[0].strip()
    line = line.split(",")[1].strip()
    state = line.split()[0]
    postal = line.split()[1]
    country_code = "US"
    store_number = "<MISSING>"
    text = "".join(
        tree.xpath(
            "//div[@class='taxonomy-description']/p[./a[contains(@href, 'map')]]/a/@href"
        )
    )
    latitude = text.split("sll=")[1].split(",")[0]
    longitude = text.split("sll=")[1].split(",")[1].split("&")[0]
    location_type = "<MISSING>"
    hours = tree.xpath("//div[@class='taxonomy-description']/p[last()]/text()")
    hours = list(filter(None, [h.strip() for h in hours]))
    hours_of_operation = ";".join(hours) or "<MISSING>"

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


def get_urls():
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0"
    }
    r = session.get("https://perryssteakhouse.com/locations/", headers=headers)
    tree = html.fromstring(r.text)

    return set(tree.xpath("//a[contains(@class, 'loc-spacer')]/@href"))


def get_data(page_url):
    locator_domain = "https://perryssteakhouse.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0"
    }

    session = SgRequests()
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//div[@class='lockup']/h3/text()")).strip()
    line = tree.xpath(
        "//div[@class='info']//span[@class='vertical'][1]/following-sibling::span/p[1]/text()"
    )
    street_address = line[0]
    line = line[1]
    city = line.split(",")[0].strip()
    line = line.split(",")[1].strip()
    state = line.split()[0]
    postal = line.split()[1]
    country_code = "US"
    store_number = "<MISSING>"
    phone = (
        "".join(
            tree.xpath("//div[@class='info']//a[contains(@href, 'tel')]/text()")
        ).strip()
        or "<MISSING>"
    )
    latitude = "".join(tree.xpath("//div[@data-lat]/@data-lat")) or "<MISSING>"
    longitude = "".join(tree.xpath("//div[@data-lng]/@data-lng")) or "<MISSING>"
    location_type = "<MISSING>"

    _tmp = []
    hours = tree.xpath("//div[@class='info']//p[@class='dine-in']")
    for h in hours:
        day = "".join(h.xpath("./text()")).strip()
        time = (
            "".join(h.xpath("./span[contains(text(), 'Dine')]/text()"))
            .replace("(Dine-In)", "")
            .strip()
        )
        _tmp.append(f"{day}: {time}")

    hours_of_operation = ";".join(_tmp) or "<MISSING>"
    if phone == "<MISSING>" and hours_of_operation == "<MISSING>":
        hours_of_operation = "Coming Soon"

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

    out.append(get_friendswood())
    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
