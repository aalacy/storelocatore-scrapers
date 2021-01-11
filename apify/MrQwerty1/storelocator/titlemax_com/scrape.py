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
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Upgrade-Insecure-Requests": "1",
    }
    r = session.get("https://www.titlemax.com/stores.xml", headers=headers)
    tree = html.fromstring(r.content)
    return tree.xpath("//loc/text()")


def get_data(page_url):
    session = SgRequests()

    locator_domain = "https://titlemax.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Upgrade-Insecure-Requests": "1",
    }

    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    sect = tree.xpath("//section[@id='storeCopy']")[0]
    location_name = "".join(tree.xpath("//h1[@itemprop='name']/text()")).strip()
    street_address = "".join(
        sect.xpath(".//div[@itemprop='streetAddress']/text()")
    ).strip()
    city = "".join(sect.xpath(".//span[@itemprop='addressLocality']/text()")).strip()
    state = "".join(sect.xpath(".//span[@itemprop='addressRegion']/text()")).strip()
    postal = sect.xpath(".//div[@class='store-address-2']/text()")[-1].strip()
    country_code = "US"
    store_number = "<MISSING>"
    phone = "".join(sect.xpath(".//span[@itemprop='telephone']/text()")).strip()
    if page_url.find("pawns") != -1:
        location_type = "Title Pawns"
    elif page_url.find("loans") != -1:
        location_type = "Title Loans"
    elif page_url.find("appraiser") != -1:
        location_type = "TitleMax Appraisals"
    else:
        location_type = "Title Loans"

    script = "".join(tree.xpath("//script[contains(text(),'L.marker')]/text()"))
    latlon = ""
    for line in script.split("\n"):
        if line.find("L.marker") != -1:
            latlon = line.split("[")[1].split("]")[0].split(",")
            break

    latitude, longitude = latlon

    _tmp = []
    hours_keys = tree.xpath("//div[contains(@class, 'storeHours')]/strong/text()")
    hours_values = tree.xpath("//div[contains(@class, 'storeHours')]/text()")
    hours_values = list(filter(None, [h.strip() for h in hours_values]))
    for k, v in zip(hours_keys, hours_values):
        _tmp.append(f"{k.strip()} {v.strip()}")

    hours_of_operation = ";".join(_tmp)

    if not hours_of_operation:
        return

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

    with futures.ThreadPoolExecutor(max_workers=2) as executor:
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
