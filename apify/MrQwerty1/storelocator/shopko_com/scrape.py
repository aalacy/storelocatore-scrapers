import csv
import json

from concurrent import futures
from lxml import html, etree
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
    r = session.get("https://www.shopko.com/sitemap.xml")
    parser = etree.XMLParser(strip_cdata=True)
    tree = etree.fromstring(r.content, parser=parser)
    root = html.fromstring(etree.tostring(tree))

    return root.xpath(
        "//loc[contains(text(), '/eye-care/') and contains(text(), 'store-')]/text()"
    )


def get_data(page_url):
    locator_domain = "https://www.shopko.com/"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[contains(text(), 'Optometric')]/text()"))

    j = json.loads(text)

    location_name = j.get("name").strip()
    a = j.get("address", {})
    street_address = a.get("streetAddress") or "<MISSING>"
    city = a.get("addressLocality") or "<MISSING>"
    state = a.get("addressRegion") or "<MISSING>"
    postal = a.get("postalCode") or "<MISSING>"
    country_code = a.get("addressCountry") or "<MISSING>"
    store_number = page_url.split("-")[-1].replace("/", "")
    phone = j.get("telephone") or "<MISSING>"
    g = j.get("geo", {})
    latitude = g.get("latitude") or "<MISSING>"
    longitude = g.get("longitude") or "<MISSING>"
    location_type = j.get("@type") or "<MISSING>"

    _tmp = []
    tr = tree.xpath("//div[@class='hours']//tr")
    for t in tr:
        day = "".join(t.xpath("./td[1]/text()")).strip()
        time = "".join(t.xpath("./td[2]/text()")).strip()
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
