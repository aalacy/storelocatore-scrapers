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


def get_coords_from_embed(text):
    try:
        latitude = text.split("!3d")[1].strip().split("!")[0].strip()
        longitude = text.split("!2d")[1].strip().split("!")[0].strip()
    except IndexError:
        latitude, longitude = "<MISSING>", "<MISSING>"

    return latitude, longitude


def get_cities():
    session = SgRequests()
    r = session.get("https://www.westchesterhealth.com/find-a-location")
    tree = html.fromstring(r.text)

    return tree.xpath("//span[@class='field-content']/a/@href")


def get_urls(slug):
    url = f"https://www.westchesterhealth.com{slug}"
    session = SgRequests()
    r = session.get(url)
    tree = html.fromstring(r.text)

    return tree.xpath("//h4/a/@href")


def get_data(slug):
    locator_domain = "https://www.westchesterhealth.com/"
    page_url = f"https://www.westchesterhealth.com{slug}"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = (
        "".join(
            tree.xpath(
                "//div[@class='locations-address']/h2[1]/text()|//div[@class='locations-address']/text()"
            )
        )
        .replace("\n", " ")
        .strip()
    )
    line = tree.xpath("//div[@class='locations-address']//text()")
    line = list(filter(None, [l.strip() for l in line]))
    for l in line:
        if l == "Address" or "<!--" in l:
            line.pop(line.index(l))

    if len(line) == 3:
        line.pop(0)

    street_address = line[0]
    line = line[-1]
    city = line.split(",")[0].strip()
    line = line.split(",")[1].strip()
    state = line.split()[0]
    postal = line.split()[1]
    country_code = "US"
    store_number = "<MISSING>"
    try:
        phone = tree.xpath("//a[contains(@href, 'tel:')]/text()")[0].strip()
    except IndexError:
        strong = tree.xpath(
            "//*[re:test(local-name(), 'strongphone*')]/text()",
            namespaces={"re": "http://exslt.org/regular-expressions"},
        )
        if strong:
            phone = strong[0].strip()
        else:
            phone = "<MISSING>"
    text = "".join(tree.xpath("//iframe/@src"))
    latitude, longitude = get_coords_from_embed(text)
    location_type = "<MISSING>"

    _tmp = []
    text = set(tree.xpath("//text()"))
    days = (
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    )
    for t in text:
        for d in days:
            if d in t:
                _tmp.append(t.strip())
                break

    if not _tmp:
        _tmp = tree.xpath("//strong[text()='Hours:']/following-sibling::text()")
        _tmp = list(filter(None, [t.strip() for t in _tmp]))

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
    urls = []
    cities = get_cities()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_urls, city): city for city in cities}
        for future in futures.as_completed(future_to_url):
            rows = future.result()
            for row in rows:
                urls.append(row)

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
