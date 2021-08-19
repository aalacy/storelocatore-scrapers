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


def get_arena_venues(page_url):
    rows = []
    locator_domain = "https://pjspub.com/"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[contains(@class, 'symple-column symple-one-fourth')]")

    for d in divs:
        location_name = "".join(
            d.xpath(".//span[contains(@style, 'color:#000;')]/text()")
        ).strip()
        line = d.xpath(".//p[@class='locationinfo']/a/text()")
        line = list(filter(None, [l.strip() for l in line]))
        if not line:
            continue

        street_address = ", ".join(line[:-1]).strip() or "<MISSING>"
        line = line[-1]
        city = line.split(",")[0].strip()
        state = line.split(",")[1].strip()
        postal = "<MISSING>"
        country_code = "US"
        store_number = "<MISSING>"
        phone = "<MISSING>"
        text = "".join(d.xpath(".//p[@class='locationinfo']/a/@href"))
        latitude, longitude = get_coords_from_google_url(text)
        location_type = "<MISSING>"
        hours_of_operation = "<MISSING>"

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

        rows.append(row)
    return rows


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
    session = SgRequests()
    r = session.get("https://pjspub.com/choose.php")
    tree = html.fromstring(r.text)

    return set(tree.xpath("//p[@class='chooselocation']/a/@href"))


def get_data(url):
    locator_domain = "https://pjspub.com/"
    page_url = f"{locator_domain}{url}"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(
        tree.xpath("//h3[@class='locationinfo-location']/text()")
    ).strip()
    line = tree.xpath(
        "//div[@id='locationinfo-address']/p[@class='locationinfo']/a/text()"
    )
    line = list(filter(None, [l.strip() for l in line]))
    if not line:
        return

    street_address = ", ".join(line[:-1]).strip() or "<MISSING>"
    line = line[-1]
    city = line.split(",")[0].strip()
    line = line.split(",")[1].strip()
    state = line.split()[0]
    postal = line.split()[1]
    country_code = "US"
    store_number = "<MISSING>"
    phone = (
        "".join(
            tree.xpath(
                "//div[@id='locationinfo-address']/p[@class='locationinfo']/text()"
            )
        )
        .replace("p.", "")
        .strip()
        or "<MISSING>"
    )

    text = "".join(
        tree.xpath("//div[@id='locationinfo-address']/p[@class='locationinfo']/a/@href")
    )
    latitude, longitude = get_coords_from_google_url(text)
    location_type = "<MISSING>"

    _tmp = []
    hours = tree.xpath(
        "//div[@id='locationinfo-hours']/p[@class='locationinfo']//text()"
    )
    hours = list(filter(None, [h.strip() for h in hours]))

    for h in hours:
        if "dine" in h.lower() or (h.startswith("(") and h.endswith(")")):
            continue
        if "(" in h:
            h = h.split("(")[0].strip() + " " + h.split(")")[1].strip()

        _tmp.append(h)

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

    rows = get_arena_venues("https://pjspub.com/about.php?loc=Arena_Venues")
    for row in rows:
        out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
