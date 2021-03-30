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
    r = session.get("https://www.orangeleafyogurt.com/locations")
    tree = html.fromstring(r.text)

    return tree.xpath("//div[@class='col-md-4 location']/h5/a/@href")


def get_data(page_url):
    locator_domain = "https://www.orangeleafyogurt.com/"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(
        tree.xpath("//div[@class='col-lg-5 info']/h2/text()")
    ).strip()
    line = tree.xpath("//div[@class='address']/text()")
    line = list(filter(None, [l.strip() for l in line]))
    phone = line[-1]
    line = line[:-1]
    part = line[-1]
    line = line[:-1]
    street_address = ", ".join(line)
    city = part.split(",")[0].strip()
    part = part.split(",")[-1].strip()
    state = part.split()[0].strip()
    postal = part.split()[-1].strip()
    country_code = "US"
    store_number = "<MISSING>"
    try:
        latlon = "".join(tree.xpath("//a[text()='Directions']/@href"))
        latitude, longitude = latlon.split("@")[-1].split(",")
    except:
        latitude, longitude = "<MISSING>", "<MISSING>"
    location_type = "<MISSING>"

    _tmp = []
    divs = tree.xpath("//div[@class='hours']/div")
    for d in divs:
        day = "".join(d.xpath("./div[1]/text()")).strip()
        time = "".join(d.xpath("./div[2]//text()")).strip()
        _tmp.append(f"{day}: {time}")

    hours_of_operation = ";".join(_tmp) or "<MISSING>"
    if location_name.lower().find("closed") != -1:
        hours_of_operation = "Temporarily Closed"

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
