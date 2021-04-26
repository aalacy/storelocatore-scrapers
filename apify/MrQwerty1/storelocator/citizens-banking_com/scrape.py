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


def get_params():
    urls, coords = list(), dict()
    session = SgRequests()
    r = session.get(
        "https://www.citizens-banking.com/Contact/About-Citizens-Bank/Locations"
    )
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@class='locations__item']")
    for d in divs:
        url = "".join(d.xpath(".//a[text()='View Details']/@href"))
        key = url.split("/")[-1]
        lat = "".join(d.xpath(".//span[@class='hide lat']/text()"))
        lng = "".join(d.xpath(".//span[@class='hide lng']/text()"))
        coords[key] = (lat, lng)
        urls.append(url)

    return urls, coords


def get_data(page_url, coords):
    locator_domain = "https://www.citizens-banking.com/"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//h1[@class='page-title']/text()")).strip()

    line = tree.xpath("//p[@class='branch-address']/text()")
    line = list(filter(None, [l.strip() for l in line]))

    street_address = ", ".join(line[:-1]).strip() or "<MISSING>"
    line = line[-1]
    city = line.split(",")[0].strip()
    line = line.split(",")[1].strip()
    state = line.split()[0]
    postal = line.split()[1]
    country_code = "US"
    store_number = "<MISSING>"
    phone_text = tree.xpath("//p[@class='branch-phone-fax']/text()")
    phone = "<MISSING>"
    for p in phone_text:
        if "P:" in p:
            phone = p.replace("P:", "").strip()
            break

    key = page_url.split("/")[-1]
    latitude, longitude = coords[key]
    location_type = "<MISSING>"

    _tmp = []
    tr = tree.xpath(
        "//div[@class='lobby-hours' and ./h2[contains(text(), 'Lobby')]]//tr"
    )

    for t in tr:
        day = "".join(t.xpath("./td[1]/text()")).strip()
        time = "".join(t.xpath("./td[2]/text()")).strip()
        _tmp.append(f"{day}: {time}")

    hours_of_operation = ";".join(_tmp) or "Coming Soon"

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
    urls, coords = get_params()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url, coords): url for url in urls}
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
