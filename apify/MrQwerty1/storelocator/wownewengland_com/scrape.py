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
    r = session.get("https://www.wownewengland.com/")
    tree = html.fromstring(r.text)

    return tree.xpath(
        "//ul[contains(@class,'sub-menu dropdown-menu')]/li[@data-depth='2']/a/@href"
    )


def get_data(page_url):
    locator_domain = "https://www.wownewengland.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    }

    session = SgRequests()
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//title/text()")).split("-")[0].strip()
    line = []
    lines = tree.xpath("//h2//span[@style='color: #ffffff;']/text()")
    for l in lines:
        if "Get" in l or "This" in l:
            break
        if l.strip():
            line.append(l.strip())

    street_address = ", ".join(line[:-1]).strip() or "<MISSING>"
    line = line[-1]
    postal = line.split()[-1]
    state = line.split()[-2]
    city = line.replace(postal, "").replace(state, "").replace(",", "").strip()
    country_code = "US"
    store_number = "<MISSING>"
    try:
        phone = tree.xpath("//h2/span[not(contains(@style, 'color: #ffffff'))]/text()")[
            0
        ].strip()
        if not phone[0].isdigit() and phone[0] != "(":
            phone = "<MISSING>"
    except IndexError:
        phone = "<MISSING>"

    latitude = "<MISSING>"
    longitude = "<MISSING>"
    location_type = "<MISSING>"

    _tmp = []
    hours = tree.xpath("//h4/span[contains(@style, 'color: #ffffff')]/text()")
    hours = list(filter(None, [h.strip() for h in hours]))
    for h in hours:
        if "hours" in h.lower() or h.startswith("("):
            continue
        _tmp.append(h.replace("|", ";").replace("\xa0", ""))

    hours_of_operation = ";".join(_tmp) or "Temporarily Closed"

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

    with futures.ThreadPoolExecutor(max_workers=1) as executor:
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
