import csv
import json

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
    r = session.get("https://www.jasonsdeli.com/restaurants")
    tree = html.fromstring(r.content)
    return tree.xpath("//div[@class='location']//a/@href")


def get_data(url):
    session = SgRequests()

    locator_domain = "https://www.jasonsdeli.com/"
    page_url = f"https://www.jasonsdeli.com{url}"

    r = session.get(page_url)
    tree = html.fromstring(r.text)
    location_name = "".join(tree.xpath("//div[@class='loc-title']/text()")).strip()
    line = tree.xpath("//div[@class='address']/text()")
    line = list(filter(None, [l.strip() for l in line]))
    street_address = line[0]
    line = line[-1]
    city = line.split(",")[0].strip() or "<MISSING>"
    line = line.split(",")[1].strip()
    postal = line.split()[-1]
    state = line.replace(postal, "").strip()
    country_code = "US"
    store_number = tree.xpath("//link[@rel='shortlink']/@href")[0].split("/")[-1]
    phone = "".join(tree.xpath("//a[@class='cnphone']/text()")) or "<MISSING>"
    if phone[0] != "(" and not phone[0].isdigit():
        phone = "<MISSING>"
    location_type = "<MISSING>"

    script = "".join(tree.xpath("""//script[contains(text(),'"center":{')]/text()"""))
    if script:
        try:
            text = script.split(""""center":""")[1].split("},")[0]
            latlon = json.loads(text)
            latlon = (latlon.get("lat"), latlon.get("lon"))
        except:
            latlon = ("<MISSING>", "<MISSING>")
    else:
        latlon = ("<MISSING>", "<MISSING>")

    latitude, longitude = latlon

    hours_of_operation = ";".join(
        tree.xpath("//div[@class='loc-hours']/p/text()")
    ).replace("\xa0", " ")

    if location_name.lower().find("permanently") != -1:
        return
    elif location_name.lower().find("temporarily") != -1:
        hours_of_operation = "Temporarily Closed"
        location_name = location_name.split("-")[0].strip()

    if (
        hours_of_operation.lower().find("vary by") != -1
        or hours_of_operation.lower() == "hours vary"
    ):
        hours_of_operation = "<MISSING>"
    elif hours_of_operation.lower().find("n/a") != -1:
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
