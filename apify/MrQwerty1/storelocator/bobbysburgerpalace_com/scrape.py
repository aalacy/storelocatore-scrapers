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
    r = session.get("http://bobbysburgerpalace.com/locations")
    tree = html.fromstring(r.text)

    return tree.xpath("//div[@id='locations-list']/p/a/@href")


def get_data(page_url):
    locator_domain = "http://bobbysburgerpalace.com/"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//div[@id='page-pad']/h3/text()")).strip()
    line = tree.xpath("//div[@id='page-pad']/p/text()")
    line = list(filter(None, [l.strip() for l in line]))

    street_address = line[0]
    phone = line[-1].replace("T:", "").strip()
    line = line[1]
    city = line.split(",")[0].strip()
    line = line.split(",")[1].strip()
    state = line.split()[0].replace(".", "")
    postal = line.split()[1]
    country_code = "US"
    store_number = page_url.split("/")[-2]
    text = "".join(
        tree.xpath("//script[contains(text(),'new google.maps.LatLng')]/text()")
    )
    try:
        latitude, longitude = eval(
            text.split("new google.maps.LatLng")[1].split(";")[0]
        )
    except:
        latitude, longitude = "<MISSING>", "<MISSING>"
    location_type = "<MISSING>"

    _tmp = []
    days = tree.xpath("//div[@class='hours-day']/text()")
    times = tree.xpath("//div[@class='hours-time']/text()")

    for d, t in zip(days, times):
        _tmp.append(f"{d.strip()} {t.strip()}")

    hours_of_operation = ";".join(_tmp) or "<MISSING>"
    if ";:" in hours_of_operation:
        hours_of_operation = hours_of_operation.split(";:")[0].strip()

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
