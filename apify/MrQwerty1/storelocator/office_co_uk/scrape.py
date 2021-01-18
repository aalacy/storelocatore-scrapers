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
    r = session.get(
        "https://www.office.co.uk/medias/sys_master/root/h17/h42/10345024454686/Store-en-GBP-9078464507453372675.xml"
    )
    tree = html.fromstring(r.content)

    return tree.xpath("//loc/text()")


def get_data(page_url):
    locator_domain = "https://www.bangor.com/"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(
        tree.xpath("//div[@class='addressDetails']/a/span/text()")
    ).strip()
    line = tree.xpath("//div[@class='addressDetails']/a/text()")
    line = list(filter(None, [l.strip() for l in line]))
    phone = "<MISSING>"

    i = 0
    for l in line:
        if l.lower().find("tel") != -1:
            phone = l.lower().replace("tel", "").replace(":", "").strip()
            break
        i += 1

    if i != len(line):
        line.remove(line[i])

    street_address = line[0]
    line = line[-1]
    postal = " ".join(line.split()[-2:])
    city = line.replace(postal, "").strip()
    if postal == line:
        city = postal
        postal = "<MISSING>"
    state = "<MISSING>"
    country_code = "GB"
    store_number = "<MISSING>"

    try:
        text = "".join(tree.xpath("//script[contains(text(), 'LatLng')]/text()"))
        latitude, longitude = eval(text.split("LatLng")[1].split(");")[0])
    except IndexError:
        latitude, longitude = "<MISSING>", "<MISSING>"
    location_type = "<MISSING>"
    hours_of_operation = (
        ";".join(
            tree.xpath("//span[@class='storelocator_open_times_day']/text()")
        ).replace("  - ", "Closed")
        or "<MISSING>"
    )
    if hours_of_operation.count("Closed") == 7:
        hours_of_operation = "Closed"

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
