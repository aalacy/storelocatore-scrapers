import csv

from concurrent import futures
from datetime import datetime
from lxml import html
from sgrequests import SgRequests
from sgscrape.sgpostal import International_Parser, parse_address


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
    r = session.get("https://www.beatone.co.uk/bars")
    tree = html.fromstring(r.text)

    return tree.xpath("//a[@class='inner-item']/@href")


def get_data(url):
    locator_domain = "https://www.beatone.co.uk/"
    page_url = f"https://www.beatone.co.uk{url}"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = tree.xpath("//h1/text()")[1].strip()
    line = " ".join(tree.xpath("//ul[@class='menu vertical address']/li/text()"))
    adr = parse_address(International_Parser(), line)

    street_address = (
        f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
            "None", ""
        ).strip()
        or "<MISSING>"
    )
    city = adr.city or "<MISSING>"
    state = adr.state or "<MISSING>"
    postal = adr.postcode or "<MISSING>"
    if postal == "<MISSING>":
        postal = " ".join(street_address.split()[-2:])
        street_address = street_address.replace(postal, "").strip()
    country_code = "GB"
    store_number = "<MISSING>"
    phone = (
        "".join(
            tree.xpath("//ul[@class='menu vertical']//a[contains(@href, 'tel')]/text()")
        ).strip()
        or "<MISSING>"
    )

    try:
        text = "".join(tree.xpath("//script[contains(text(), 'new H.Map(')]/text()"))
        text = text.split("center: ")[1].split("});")[0].strip()
        lat, lng = "lat", "lng"
        a = eval(text)
        latitude = a.get(lat) or "<MISSING>"
        longitude = a.get(lng) or "<MISSING>"
    except:
        latitude = "<MISSING>"
        longitude = "<MISSING>"
    location_type = "<MISSING>"

    _tmp = []
    divs = tree.xpath("//div[@class='opening-times']/div[./span]")
    for d in divs:
        day = "".join(d.xpath("./span/text()")).strip()
        time = "".join(d.xpath("./text()")).strip()
        _tmp.append(f"{day} {time}")

    hours_of_operation = (
        ";".join(_tmp).replace("Today", datetime.today().strftime("%A")) or "<MISSING>"
    )
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
