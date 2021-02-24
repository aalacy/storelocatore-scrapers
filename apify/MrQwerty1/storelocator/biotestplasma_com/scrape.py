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
    r = session.get("https://www.grifolsplasma.com/en/locations/find-a-donation-center")
    tree = html.fromstring(r.text)

    return set(tree.xpath("//div[contains(@class,'nearby-center-detail')]/a/@href"))


def get_data(page_url):
    locator_domain = "https://www.grifolsplasma.com/"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    if r.url != page_url:
        return

    location_name = "".join(
        tree.xpath("//div[@class='center-address']/h2/text()")
    ).strip()
    line = tree.xpath("//div[@class='center-address']/p[not(@class)]/text()")
    street_address = ", ".join(line[:-1]).strip()
    line = line[-1]
    city = line.split(",")[0].strip()
    line = "".join(line.split(",")[1:]).strip()
    state = line.split()[0]
    postal = line.split()[1]
    country_code = "US"
    store_number = "<MISSING>"
    phone = (
        "".join(tree.xpath("//p[@class='telephone desktop']/text()")).strip()
        or "<MISSING>"
    )
    text = "".join(
        tree.xpath("//script[contains(text(), 'new google.maps.LatLng')]/text()")
    )
    try:
        latitude = text.split(";")[3].split("=")[-1].replace("+", "")
        longitude = text.split(";")[4].split("=")[-1]
    except IndexError:
        latitude, longitude = "<MISSING>", "<MISSING>"
    location_type = "<MISSING>"

    _tmp = []
    hours = tree.xpath("//p[@class='hours']")

    for h in hours:
        day = "".join(h.xpath("./span[1]//text()")).strip()
        time = "".join(h.xpath("./span[2]//text()")).strip()
        _tmp.append(f"{day} {time}")

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
