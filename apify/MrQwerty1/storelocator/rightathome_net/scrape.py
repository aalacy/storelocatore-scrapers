import csv
import re

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
    urls = []
    session = SgRequests()
    r = session.get("https://www.rightathome.net/states")
    tree = html.fromstring(r.content)
    states = tree.xpath("//ul[@class='state-list']/li/a/@href")
    for state in states:
        if state.startswith("/"):
            state = f"https://www.rightathome.net{state}"

        r = session.get(state)
        tree = html.fromstring(r.text)
        links = tree.xpath("//div[@class='col-sm-8']/h5[@class='entry-title']/a/@href")
        urls += links

    return urls


def get_data(u):
    session = SgRequests()
    r = session.get(u)
    tree = html.fromstring(r.text)
    regex = r"(\d{5}$|\d{5}-\d+?$)"
    locator_domain = "https://www.rightathome.net"
    location_name = (
        "".join(tree.xpath("//p[@class='page-description']/text()"))
        .replace("-", "")
        .strip()
    )
    line = tree.xpath("//div[@style='float:left']")[0].xpath(".//text()")
    line = list(filter(None, [l.strip() for l in line]))
    i = 0
    for l in line:
        if re.findall(regex, l):
            break
        i += 1

    part_line = line[i]
    street_address = ", ".join(line[:i])
    city = part_line.split(",")[0].strip()
    if not location_name:
        location_name = f"Right at Home in {city}"
    state = part_line.split(",")[1].strip()[:2]
    postal = part_line.split(",")[1].split()[-1]
    phone = tree.xpath("//div[@class='mobiletel']/a/text()")[0]
    try:
        text = "".join(tree.xpath("//script[contains(text(),'@type')]/text()"))
        latitude = re.findall(r'"latitude": "(\d{2,3}.\d+)"', text)[0]
        longitude = re.findall(r'"longitude": "(-?\d{2,3}.\d+)"', text)[0]
    except:
        latitude = "<MISSING>"
        longitude = "<MISSING>"
    page_url = u
    country_code = "US"
    store_number = "<MISSING>"
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

    return row


def fetch_data():
    out = []
    s = set()
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url): url for url in urls}
        for future in futures.as_completed(future_to_url):
            row = future.result()
            line = tuple(row[2:6])
            if row and line not in s:
                s.add(line)
                out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
