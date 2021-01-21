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
    urls = []
    session = SgRequests()
    r = session.get(
        "https://www.eehealth.org/mapi/public/LocationSearch.json?label=d6731d49-dfcb-4082-bb26-7e7b62940469&start=0&count=5000"
    )
    js = r.json()["response"]["locations"]
    for j in js:
        urls.append(f'https://www.eehealth.org{j.get("locationUrl")}')

    return urls


def get_data(page_url):
    locator_domain = "https://www.eehealth.org/"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(
        tree.xpath("//div[@class='location-detail__title']/h1/text()")
    ).strip()
    adr1 = "".join(
        tree.xpath("//span[@class='location-detail__address-one']/text()")
    ).strip()
    adr2 = "".join(
        tree.xpath("//span[@class='location-detail__address-two']/text()")
    ).strip()
    street_address = f"{adr1} {adr2}".strip() or "<MISSING>"
    city = (
        "".join(
            tree.xpath("//span[@class='location-detail__address-city']/text()")
        ).strip()
        or "<MISSING>"
    )
    if street_address.find(city) != -1:
        street_address = street_address.split(city)[0].strip()
    state = (
        "".join(
            tree.xpath("//span[@class='location-detail__address-state']/text()")
        ).strip()
        or "<MISSING>"
    )
    postal = (
        "".join(
            tree.xpath("//span[@class='location-detail__address-zip']/text()")
        ).strip()
        or "<MISSING>"
    )
    country_code = "US"
    store_number = "<MISSING>"
    phone = (
        "".join(tree.xpath("//span[@class='location-detail__main-phone']/text()"))
        .replace("(CARE)", "")
        .strip()
        or "<MISSING>"
    )
    if phone.find(":") != -1:
        phone = phone.split(":")[1].strip()
    if phone == "<MISSING>":
        phone = (
            "".join(
                tree.xpath("//p[./strong[contains(text(), 'Main Phone')]]/text()")
            ).strip()
            or "<MISSING>"
        )
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    location_type = "<MISSING>"

    _tmp = []
    pp = tree.xpath("//span[@class='location-detail__office-hours']/p[1]/text()")
    pp = list(filter(None, [p.strip() for p in pp]))

    for p in pp:
        if len(p) > 1:
            _tmp.append(p)

    hours_of_operation = ";".join(_tmp) or "<MISSING>"

    if hours_of_operation == "<MISSING>":
        hours_of_operation = (
            "".join(tree.xpath("//span[@class='location-detail__office-hours']/text()"))
            .strip()
            .replace("\n", ";")
            or "<MISSING>"
        )

    if hours_of_operation.lower().find("call") != -1:
        hours_of_operation = "<MISSING>"

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
