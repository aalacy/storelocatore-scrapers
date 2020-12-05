import csv

from concurrent.futures import ThreadPoolExecutor, as_completed
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
    r = session.get("https://thelearningexperience.com/centers-sitemap.xml")
    tree = html.fromstring(r.content)
    return tree.xpath("//loc/text()")[1:]


def get_data(page_url):
    session = SgRequests()

    locator_domain = "https://thelearningexperience.com/"

    r = session.get(page_url)
    tree = html.fromstring(r.text)
    location_name = "".join(tree.xpath("//title/text()")).strip()
    line = tree.xpath("//p[@class='address']/text()")
    line = list(filter(None, [l.strip() for l in line]))
    street_address = line[0]
    if street_address.find("(") != -1:
        street_address = street_address.split("(")[0].strip()
    if street_address == ", ,":
        street_address = "<MISSING>"
    line = line[-1]
    city = line.split(",")[0].strip() or "<MISSING>"
    state = line.split(",")[1].strip() or "<MISSING>"
    postal = line.split(",")[2].strip() or "<MISSING>"
    country_code = "US"
    store_number = "<MISSING>"
    phone = (
        "".join(
            tree.xpath("//p[@class='phone']/a[contains(@href, 'tel:')]/text()")
        ).strip()
        or "<MISSING>"
    )
    location_type = "<MISSING>"

    script = "".join(
        tree.xpath("//a[contains(@href, 'http://maps.google.com/maps?q=')]/@href")
    )
    if script:
        try:
            latlon = eval(
                "(" + script.replace("http://maps.google.com/maps?q=", "") + ")"
            )

            if latlon == (0.000000000, 0.000000000):
                latlon = ("<MISSING>", "<MISSING>")
        except:
            latlon = ("<MISSING>", "<MISSING>")
    else:
        latlon = ("<MISSING>", "<MISSING>")

    latitude, longitude = latlon

    hours = tree.xpath("//p[contains(text(), 'Monday')]/text()")
    hours = list(filter(None, [h.strip() for h in hours]))

    if hours:
        hours_of_operation = f"{hours[0]}: {hours[1]}"
    else:
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

    return row


def fetch_data():
    out = []
    threads = []
    urls = get_urls()

    with ThreadPoolExecutor(max_workers=10) as executor:
        for url in urls:
            threads.append(executor.submit(get_data, url))

    for task in as_completed(threads):
        row = task.result()
        if row:
            out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
