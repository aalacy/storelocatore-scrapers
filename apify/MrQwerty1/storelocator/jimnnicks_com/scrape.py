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
    urls = set()
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0"
    }
    r = session.get("https://www.jimnnicks.com/locations-sitemap.xml", headers=headers)
    tree = html.fromstring(r.content)
    links = tree.xpath(
        "//loc[contains(text(), 'https://www.jimnnicks.com/locations/')]/text()"
    )
    for link in links:
        if link.count("/") == 7:
            urls.add(link)

    return urls


def get_data(page_url):
    locator_domain = "https://www.jimnnicks.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0"
    }

    session = SgRequests()
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//h1/text()")).replace("\n", " - ").strip()
    line = tree.xpath("//address/text()")
    line = list(filter(None, [l.strip() for l in line]))

    street_address = ", ".join(line[:-1]).strip()
    line = line[-1]
    city = line.split(",")[0].strip()
    line = line.split(",")[1].strip()
    state = line.split()[0]
    postal = line.split()[1]
    country_code = "US"
    store_number = "<MISSING>"
    phone = (
        "".join(
            tree.xpath(
                "//div[./div/span[text()= 'Phone']]/following-sibling::div[1]//a/text()"
            )
        ).strip()
        or "<MISSING>"
    )
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    location_type = "<MISSING>"

    _tmp = []
    divs = tree.xpath("//div[./span[@class='weekday']]")

    for d in divs:
        day = "".join(d.xpath("./span/text()")).strip()
        time = " - ".join(d.xpath("./time/text()")).strip()
        _tmp.append(f"{day}: {time}")

    hours_of_operation = ";".join(_tmp) or "<MISSING>"
    if "coming" in location_name.lower():
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

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
