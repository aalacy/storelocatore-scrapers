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
    r = session.get("https://www.hendrickcars.com/hendrick-collision.htm")
    tree = html.fromstring(r.text)

    return tree.xpath(
        "//button/a[text()='Learn More']/@href|//a[./button[text()='Learn More']]/@href"
    )


def get_data(url):
    locator_domain = "https://www.hendrickcars.com/"
    page_url = f"https://www.hendrickcars.com{url}"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//h2[@id='content1-heading']/text()")).strip()
    street_address = (
        tree.xpath("//span[@class='street-address']/text()")[0].strip() or "<MISSING>"
    )
    city = tree.xpath("//span[@class='locality']/text()")[0].strip() or "<MISSING>"
    state = tree.xpath("//span[@class='region']/text()")[0].strip() or "<MISSING>"
    postal = tree.xpath("//span[@class='postal-code']/text()")[0].strip() or "<MISSING>"
    country_code = "US"
    store_number = "<MISSING>"
    phone = (
        "".join(tree.xpath("//li[@data-click-to-call-phone]/@data-click-to-call-phone"))
        or "<MISSING>"
    )
    if "?" in phone:
        phone = phone.split("?")[0].strip()
    coords = (
        "".join(tree.xpath("//div[@data-markers-list]/@data-markers-list")).replace(
            " ", ""
        )
        or "[[<MISSING>,<MISSING>]]"
    )
    latitude, longitude = coords.replace("[", "").replace("]", "").split(",")
    location_type = "<MISSING>"

    _tmp = []
    days = tree.xpath("//li[@class='clearfix' or @class='clearfix today']")
    for d in days:
        day = "".join(d.xpath("./span[1]/text()")).strip()
        time = "".join(d.xpath("./span[2]/text()")).strip()
        if "(" in time:
            time = time.split("(")[0].strip()
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

    with futures.ThreadPoolExecutor(max_workers=11) as executor:
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
