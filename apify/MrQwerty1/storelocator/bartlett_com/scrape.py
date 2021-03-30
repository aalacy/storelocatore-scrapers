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


def get_lines():
    lines = []
    session = SgRequests()
    r = session.get("https://www.bartlett.com/bartlett-offices.cfm")
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@class='col-xs-12 col-sm-6 col-md-4 list-group-item']")
    for d in divs:
        check = "".join(d.xpath("./@data-oname"))
        if check.find(",") == -1:
            continue
        lat = "".join(d.xpath("./@data-lat")) or "<MISSING>"
        lng = "".join(d.xpath("./@data-lng")) or "<MISSING>"
        url = f'https://www.bartlett.com{"".join(d.xpath(".//h5/a/@href"))}'
        line = (url, (lat, lng))
        lines.append(line)

    return lines


def get_data(line):
    page_url = line[0]
    locator_domain = "https://www.bartlett.com/"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = " ".join("".join(tree.xpath("//h1/text()")).split())
    street_address = (
        "".join(tree.xpath("//span[@class='street-address']/text()")).strip()
        or "<MISSING>"
    )
    city = (
        "".join(tree.xpath("//span[@class='locality']/text()")).strip() or "<MISSING>"
    )
    state = "".join(tree.xpath("//span[@class='region']/text()")).strip() or "<MISSING>"
    postal = (
        "".join(tree.xpath("//span[@class='postcode']/text()")).strip() or "<MISSING>"
    )
    if len(postal) == 5 or postal.find("-") != -1:
        country_code = "US"
    else:
        country_code = "CA"
    store_number = "<MISSING>"
    try:
        phone = tree.xpath(
            "//div[@class='cell-xs-10']//a[contains(@href, 'tel')]/text()"
        )[0]
    except IndexError:
        phone = "<MISSING>"
    latitude, longitude = line[1]
    location_type = "<MISSING>"

    hours = tree.xpath(
        "//div[@class='cell-xs-10' and ./h6[text()='Office Hours']]//p[@class='text-lg-left lm-0']/text()"
    )
    hours = list(filter(None, [h.strip() for h in hours]))
    hours_of_operation = " ".join(hours) or "<MISSING>"

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
    lines = get_lines()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, line): line for line in lines}
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
