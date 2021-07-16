import csv

from concurrent import futures
from lxml import html
from sgrequests import SgRequests
from sgscrape.sgpostal import parse_address, International_Parser


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
    r = session.get("https://www.cariloha.com/stores")
    tree = html.fromstring(r.text)

    return tree.xpath("//h3[@class='store-region']/following-sibling::p//a/@href")


def get_data(page_url):
    locator_domain = "https://www.cariloha.com/"

    session = SgRequests()
    r = session.get(page_url)
    if page_url != r.url:
        return

    tree = html.fromstring(r.text)
    location_name = "".join(tree.xpath("//h1/text()")).strip()
    line = tree.xpath("//h3[contains(text(), 'Address')]/following-sibling::p//text()")
    line = ", ".join(list(filter(None, [l.strip() for l in line])))
    print(page_url, ":", line)

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
    country_code = adr.country or "<MISSING>"
    store_number = "<MISSING>"
    phone = (
        "".join(
            tree.xpath(
                "//h3[contains(text(), 'Contact')]/following-sibling::a[not(contains(@href, '@'))]/@href"
            )
        ).replace("tel:", "")
        or "<MISSING>"
    )
    latitude = (
        "".join(tree.xpath("//div[@data-latitude]/@data-latitude")) or "<MISSING>"
    )
    longitude = (
        "".join(tree.xpath("//div[@data-latitude]/@data-longitude")) or "<MISSING>"
    )
    location_type = "<MISSING>"

    _tmp = []
    tr = tree.xpath("//tr[@class='hours-row']")
    for t in tr:
        day = "".join(t.xpath("./td[1]//text()")).strip()
        time = "".join(t.xpath("./td[2]//text()")).strip()
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
