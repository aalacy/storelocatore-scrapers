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
    r = session.get("https://www.blazingonion.com/")
    tree = html.fromstring(r.text)

    return tree.xpath(
        "//a[contains(@href, '/locations')]/following-sibling::ul//a/@href"
    )


def get_data(page_url):
    locator_domain = "https://www.blazingonion.com/"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(
        tree.xpath("//h3[contains(@id, 'ctl01_rptAddresses_ctl00_lblCaption')]/text()")
    ).strip()
    street_address = (
        "".join(
            tree.xpath("//p[@id='ctl01_rptAddresses_ctl00_pAddressInfo']/text()")
        ).strip()
        or "<MISSING>"
    )
    if street_address.endswith(","):
        street_address = street_address[:-1]
    line = "".join(
        tree.xpath("//p[@id='ctl01_rptAddresses_ctl00_pStateZip']/text()")
    ).strip()
    city = line.split(",")[0].strip()
    line = line.split(",")[1].strip()
    state = line.split()[0]
    postal = line.split()[1]
    country_code = "US"
    store_number = "<MISSING>"
    phone = (
        "".join(tree.xpath("//p[@id='ctl01_rptAddresses_ctl00_pPhonenum']/text()"))
        .replace("Phone", "")
        .replace(".", "")
        .strip()
        or "<MISSING>"
    )
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    location_type = "<MISSING>"

    _tmp = []
    hours = tree.xpath("//p[contains(@class,'fp-el')]//text()")
    hours = list(filter(None, [h.strip() for h in hours]))

    rec = False
    for h in hours:
        if "Sports Lounge:" in h or "Whiskey Bar:" in h:
            break
        if "Sports Lounge" in h:
            rec = False
        if rec:
            _tmp.append(h.replace(",", ""))
        if (
            h == "Restaurant and Lounge Hours:"
            or h == "Restaurant Hours:"
            or h == "Restaurant:"
        ):
            rec = True

    hours_of_operation = ";".join(_tmp) or "<MISSING>"
    if "We" in hours_of_operation:
        hours_of_operation = hours_of_operation.split("We")[0]
    if "There's" in hours_of_operation:
        hours_of_operation = hours_of_operation.split("There's")[0]

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
