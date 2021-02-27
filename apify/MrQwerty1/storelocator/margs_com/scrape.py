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


def get_coords_from_google_url(url):
    try:
        if url.find("ll=") != -1:
            latitude = url.split("ll=")[1].split(",")[0]
            longitude = url.split("ll=")[1].split(",")[1].split("&")[0]
        else:
            latitude = url.split("@")[1].split(",")[0]
            longitude = url.split("@")[1].split(",")[1]
    except IndexError:
        latitude, longitude = "<MISSING>", "<MISSING>"

    return latitude, longitude


def get_urls():
    urls = []
    session = SgRequests()
    r = session.get("https://www.margs.com/locations")
    tree = html.fromstring(r.text)
    states = tree.xpath("//h2/a/@href")
    for state in states:
        r = session.get(state)
        root = html.fromstring(r.text)
        urls += root.xpath("//a[./span[contains(text(),'INFO & ORDER NOW')]]/@href")

    return urls


def get_data(page_url):
    locator_domain = "https://www.margs.com/"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//title/text()")).split("|")[0].strip()
    line = tree.xpath(
        "//h2[.//span[contains(text(), 'Phone')] or ./span[contains(text(), 'Phone')]]/preceding-sibling::h2/span//text()"
    )
    street_address = line[0]
    line = line[-1].replace("\xa0", " ")
    city = line.split(",")[0].strip()
    line = line.split(",")[1].strip()
    postal = line.split()[-1]
    state = line.replace(postal, "").strip()
    country_code = "US"
    store_number = "<MISSING>"
    phone = (
        "".join(
            tree.xpath(
                "//h2[.//span[contains(text(), 'Phone')] or ./span[contains(text(), 'Phone')]]//text()"
            )
        )
        .replace("Phone:", "")
        .strip()
    )
    try:
        text = tree.xpath("//a[contains(@href, 'google')]/@href")[0]
        latitude, longitude = get_coords_from_google_url(text)
    except IndexError:
        latitude, longitude = "<MISSING>", "<MISSING>"
    location_type = "<MISSING>"

    _tmp = []
    h2 = tree.xpath(
        "//h2[.//span[contains(text(), 'Sunday')]]|//h2[.//span[contains(text(), 'Sunday')]]/following-sibling::h2|//p[.//span[contains(text(), 'Sunday')]]|//p[.//span[contains(text(), 'Sunday')]]/following-sibling::h2"
    )[:7]

    for h in h2:
        line = " ".join("".join(h.xpath(".//text()")).split())
        _tmp.append(line)

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
