import csv

from concurrent import futures
from lxml import html
from sgrequests import SgRequests
from sgscrape.sgpostal import International_Parser, parse_address


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
    r = session.get("https://www.peacocks.co.uk/store-finder")
    tree = html.fromstring(r.text)

    return set(tree.xpath("//div[@class='store']/a/@href"))


def get_data(url):
    locator_domain = "https://www.peacocks.co.uk/"
    page_url = f"https://www.peacocks.co.uk{url}"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//h1/text()")).strip()
    line = "".join(tree.xpath("//div[@class='FF_grid-65']/p[1]/text()"))
    line = line.replace(", ,", ",").replace(",,", ",").strip()
    try:
        postal = line.split(",")[-1].strip()
    except IndexError:
        postal = ""
    line = ",".join(line.split(",")[:-1])
    adr = parse_address(International_Parser(), line, postcode=postal)

    street_address = (
        f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
            "None", ""
        ).strip()
        or "<MISSING>"
    )
    if len(street_address) <= 5:
        try:
            street_address = line.split(",")[0].strip()
        except IndexError:
            street_address = "<MISSING>"

    city = adr.city or "<MISSING>"
    state = adr.state or "<MISSING>"
    postal = adr.postcode or "<MISSING>"
    country_code = "GB"
    store_number = page_url.split("/")[-2]
    phone = (
        "".join(tree.xpath("//*[contains(text(), 'Tel:')]/text()"))
        .replace("Tel:", "")
        .replace("TBC", "")
        .strip()
        or "<MISSING>"
    )
    text = "".join(tree.xpath("//script[contains(text(), 'popupInitMap(')]/text()"))
    try:
        text = text.split("popupInitMap(")[1].split(")")[0]
        latitude = text.split(",")[0].strip()
        if latitude == "0":
            latitude = "<MISSING>"
        longitude = text.split(",")[1].strip()
        if longitude == "0":
            longitude = "<MISSING>"
    except IndexError:
        latitude, longitude = "<MISSING>", "<MISSING>"
    location_type = "<MISSING>"

    _tmp = []
    li = tree.xpath("//ul[@class='opening-hours']/li")

    for l in li:
        line = l.xpath(".//text()")
        line = list(filter(None, [h.strip() for h in line]))
        _tmp.append(" ".join(line))

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
    s = set()
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url): url for url in urls}
        for future in futures.as_completed(future_to_url):
            row = future.result()
            if row:
                check = row[2]
                if check not in s:
                    s.add(check)
                    out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
