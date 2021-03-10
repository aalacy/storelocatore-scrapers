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


def get_divs():
    session = SgRequests()
    r = session.get("https://www.hollywoodbowl.co.uk/centres")
    tree = html.fromstring(r.text)

    return tree.xpath("//div[@class='centre-data__item']")


def remove_comma(text):
    if text.endswith(","):
        return text[:-1]
    return text


def get_data(div):
    locator_domain = "https://www.hollywoodbowl.co.uk/"
    page_url = "".join(div.xpath("./@data-link"))

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(div.xpath("./@data-name"))
    street_address = (
        remove_comma(
            "".join(tree.xpath("//span[@itemprop='streetAddress']/p/text()")).strip()
        )
        or "<MISSING>"
    )
    city = (
        remove_comma(
            "".join(tree.xpath("//p[@itemprop='addressLocality']/text()")).strip()
        )
        or "<MISSING>"
    )
    state = (
        remove_comma(
            "".join(tree.xpath("//p[@itemprop='addressRegion']/text()")).strip()
        )
        or "<MISSING>"
    )
    postal = (
        remove_comma("".join(tree.xpath("//p[@itemprop='postalCode']/text()")).strip())
        or "<MISSING>"
    )
    country_code = "GB"
    store_number = "<MISSING>"
    phone = (
        "".join(tree.xpath("//p[@itemprop='telephone']/text()")).strip() or "<MISSING>"
    )
    latitude = "".join(div.xpath("./@data-lat")) or "<MISSING>"
    longitude = "".join(div.xpath("./@data-lng")) or "<MISSING>"
    location_type = "<MISSING>"

    _tmp = []
    tr = tree.xpath("//table[@class='opening-times']//tr")
    for t in tr:
        day = "".join(t.xpath("./th/text()")).strip()
        time = "".join(t.xpath("./td/text()")).strip()
        _tmp.append(f"{day}: {time}")

    hours_of_operation = ";".join(_tmp) or "<MISSING>"
    if hours_of_operation.lower().count("closed") == 7:
        hours_of_operation = "Closed"

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
    divs = get_divs()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, div): div for div in divs}
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
