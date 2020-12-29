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
    r = session.get("http://www.memorialhermann.org/mh-sitemap.xml")
    tree = html.fromstring(r.content)
    links = tree.xpath(
        "//loc[contains(text(), 'http://www.memorialhermann.org/locations/')]/text()"
    )

    for l in links:
        if l.count("/") != 5:
            continue
        urls.append(l)

    return urls


def clean_phone(phone):
    _tmp = []
    for p in phone:
        if p.isdigit():
            _tmp.append(p)

    if len(_tmp) < 10:
        return "<MISSING>"

    return "".join(_tmp)


def get_data(page_url):
    locator_domain = "http://www.memorialhermann.org/"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    check = "".join(tree.xpath("//div[@class='shadowbox-top-orange']/text()")).strip()
    if check:
        location_name = (
            "".join(
                tree.xpath(
                    "//p[@id='ctl00_ContentBody_uxBreadCrumbAddTitle_pLargeTopHeader']/text()"
                )
            )
            or "<MISSING>"
        )
        if location_name == "Locations":
            location_name = "".join(tree.xpath("//title/text()")).strip() or "<MISSING>"
        line = tree.xpath(
            "//div[.//div[contains(text(), 'Location ')]]/div[@class='shadowbox-bottom-orange']/p[1]//text()"
        )
        line = list(filter(None, [l.strip() for l in line]))
        street_address = line[0]
        if page_url.find("/cypress/") != -1:
            street_address = line[1]
            location_name = line[0]
        phone = clean_phone(line[-1])
        line = line[-2]
    else:
        location_name = "".join(tree.xpath("//h1/text()")) or "<MISSING>"
        line = tree.xpath("//li[@id='map']/p/text()")
        line = list(filter(None, [l.strip() for l in line]))
        street_address = line[0]
        phone = (
            tree.xpath("//li[@id='contact']/p[contains(text(), 'tel')]/text()")[-1]
            or ""
        )
        if not phone:
            phone = "".join(tree.xpath("//li[@id='contact']/p[1]/text()")) or ""
        phone = clean_phone(phone)
        line = line[-1]

    city = line.split(",")[0].strip()
    line = line.split(",")[1].strip()
    state = line.split()[0].strip()
    postal = line.split()[1].strip()

    country_code = "US"
    store_number = "<MISSING>"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    location_type = "<MISSING>"
    hours_of_operation = (
        ";".join(tree.xpath("//div[./a[@id='exit']]//li/text()")) or "<MISSING>"
    )

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
    s = set()
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url): url for url in urls}
        for future in futures.as_completed(future_to_url):
            try:
                row = future.result()
            except:
                row = []
            if row:
                check = tuple(row[2:6])
                if check not in s:
                    s.add(check)
                    out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
