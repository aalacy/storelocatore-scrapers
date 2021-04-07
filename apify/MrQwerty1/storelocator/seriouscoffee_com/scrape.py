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
    r = session.get("https://www.seriouscoffee.com/locations/")
    tree = html.fromstring(r.text)
    states = tree.xpath("//div[@class='cms_locations_name']/a/@href")
    for state in states:
        r = session.get(f"https://www.seriouscoffee.com{state}")
        tree = html.fromstring(r.text)
        links = tree.xpath("//div[@class='cms_ldirectory_name']/a/@href")

        for link in links:
            urls.append(f"https://www.seriouscoffee.com{link}")

    return urls


def get_data(page_url):
    locator_domain = "https://www.seriouscoffee.com/"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(
        tree.xpath("//div[@class='cms_locations_maincontent']/h1/text()")
    ).strip()
    line = tree.xpath("//div[@class='location_address']/text()")
    line = list(filter(None, [l.strip() for l in line]))

    street_address = line[-2]
    line = line[-1]
    city = line.split(",")[0].strip()
    line = line.split(",")[1].strip()
    state = line.split()[0]
    postal = line.replace(state, "").strip()
    country_code = "CA"
    store_number = "<MISSING>"
    phone = (
        "".join(
            tree.xpath("//b[text()='Telephone:']/following-sibling::text()[1]")
        ).strip()
        or "<MISSING>"
    )
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    location_type = "<MISSING>"

    _tmp = []
    tr = tree.xpath("//table[@class='locations_timetable_table']//tr")

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
