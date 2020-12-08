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


def get_ids():
    ids = []
    session = SgRequests()
    r = session.get("https://www.soul-cycle.com/studios/all/partial/")
    tree = html.fromstring(r.text)
    links = tree.xpath("//a[@class='studio-link']/@href")
    for l in links:
        ids.append(f"https://www.soul-cycle.com{l}")

    return ids


def clean_adr(text):
    # rule 1 - Remove any info in parentheses
    if text.find("(") != -1:
        text = text.split("(")[0].strip()

    # rule 2 - Split address by ',' and takes the first component that starts with a number
    if text.find(",") != -1:
        lines = text.split(",")
        for line in lines:
            if line.strip()[0].isdigit():
                text = line.strip()
                break

    # rule 3 - Split address by ':' and takes the first component that starts with a number
    if text.find(":") != -1:
        lines = text.split(":")
        for line in lines:
            if line.strip()[0].isdigit():
                text = line.strip()
                break

    return text


def get_data(_id):
    locator_domain = "https://soul-cycle.com/"
    page_url = _id

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    d = tree.xpath("//div[@class='studio-location-container']")[0]
    location_name = "".join(tree.xpath("//h1[@class='studio-name']/@data-studio-name"))
    street_address = clean_adr(
        "".join(d.xpath(".//span[@itemprop='streetAddress']/text()"))
    )
    city = "".join(d.xpath(".//span[@itemprop='addressLocality']/text()"))
    state = "".join(d.xpath(".//span[@itemprop='addressRegion']/text()"))
    postal = (
        "".join(d.xpath(".//span[@class='studio-location']/text()"))
        .replace(",", "")
        .strip()
    )

    if len(postal) == 5:
        country_code = "US"
    else:
        if city == "London":
            return
        else:
            country_code = "CA"

    phone = "".join(d.xpath(".//a[@itemprop='telephone']/text()"))
    store_number = "".join(d.xpath(".//a[@itemprop='telephone']/@data-studio-id"))
    location_type = "<MISSING>"
    hours_of_operation = "<MISSING>"

    line = "".join(
        tree.xpath("//script[contains(text(), 'var myLatlng')]/text()")
    ).split("\n")
    _tmp = ""
    for l in line:
        if l.find("var myLatlng =") != -1:
            _tmp = l
            break

    if _tmp:
        latitude = _tmp.split("(")[1].split(",")[0]
        longitude = _tmp.split("(")[1].split(",")[1].split(")")[0]
    else:
        latitude = "<MISSING>"
        longitude = "<MISSING>"

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
    ids = get_ids()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, _id): _id for _id in ids}
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
