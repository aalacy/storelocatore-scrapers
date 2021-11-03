import csv
import json

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
    r = session.get(
        "https://www.lequipeur.com/fr/sitemap-stores-01.xml", headers=headers
    )
    tree = html.fromstring(r.content)

    return tree.xpath("//loc/text()")


def get_data(page_url):
    locator_domain = "https://www.lequipeur.com/"
    page_url = page_url.replace("/fr/", "/en/").replace(".html", "")

    try:
        r = session.get(page_url, headers=headers, timeout=20)
        tree = html.fromstring(r.text)
        location_name = "".join(
            tree.xpath("//h2[@class='store-info__title']/text()")
        ).strip()
        text = "".join(tree.xpath("//div[@data-info]/@data-share-data"))
        j = json.loads(text)
    except:
        return

    a = j.get("address")
    street_address = f'{a.get("line1")}, {a.get("line2") or ""}'.strip() or "<MISSING>"
    if street_address.endswith(","):
        street_address = street_address[:-1]
    city = a.get("town") or "<MISSING>"
    state = a.get("province") or "<MISSING>"
    postal = a.get("postalCode") or "<MISSING>"
    country_code = "CA"
    store_number = (
        "".join(tree.xpath("//a[@class='store-info__phone']/@data-id")) or "<MISSING>"
    )
    phone = (
        "".join(tree.xpath("//a[@class='store-info__phone']/text()")).strip()
        or "<MISSING>"
    )
    try:
        line = j.get("directionLink") or "<MISSING>,<MISSING>"
        latitude, longitude = line.split("=")[-1].split(",")
    except:
        latitude, longitude = "<MISSING>", "<MISSING>"
    location_type = "<MISSING>"
    hours = tree.xpath(
        "//ul[@class='store-info__section-list js-drop-down__content']/p/text()"
    )
    hours = list(filter(None, [h.strip() for h in hours]))
    hours_of_operation = ";".join(hours).strip() or "<MISSING>"

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

    with futures.ThreadPoolExecutor(max_workers=20) as executor:
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
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "uk-UA,uk;q=0.8,en-US;q=0.5,en;q=0.3",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "max-age=0",
        "TE": "Trailers",
    }
    scrape()
