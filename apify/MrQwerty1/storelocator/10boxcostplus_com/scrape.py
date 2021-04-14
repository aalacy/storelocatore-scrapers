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
    r = session.get(
        "https://www.10boxcostplus.com/StoreLocator/Search/?ZipCode=75022&miles=5000"
    )
    tree = html.fromstring(r.text)

    return tree.xpath("//td/a[contains(@href, 'Store_Detail_S.las?L=')]/@href")


def get_data(page_url):
    locator_domain = "https://www.10boxcostplus.com/"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(
        tree.xpath("//div[@class='row']/following-sibling::h3/text()")
    ).strip()
    line = tree.xpath("//p[@class='Address']/text()")
    line = list(filter(None, [l.strip() for l in line]))

    street_address = ", ".join(line[:-1]).strip()
    line = line[-1]
    city = line.split(",")[0].strip()
    line = line.split(",")[1].strip()
    state = line.split()[0]
    postal = line.split()[1]
    country_code = "US"
    store_number = page_url.split("L=")[1].split("&")[0]
    phone = tree.xpath("//p[@class='PhoneNumber']/a/text()")[0].strip() or "<MISSING>"

    try:
        text = "".join(tree.xpath("//script[contains(text(), 'initializeMap')]/text()"))
        latitude, longitude = eval(text.split("initializeMap")[1].split(";")[0])
        if not latitude:
            latitude, longitude = "<MISSING>", "<MISSING>"
    except:
        latitude, longitude = "<MISSING>", "<MISSING>"
    location_type = "<MISSING>"
    hours_of_operation = (
        ";".join(
            tree.xpath(
                "//dt[text()='Hours of Operation:']/following-sibling::dd[1]/text()"
            )
        )
        or "<MISSING>"
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
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=12) as executor:
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
