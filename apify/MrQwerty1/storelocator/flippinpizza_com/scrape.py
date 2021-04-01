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


def get_hours(yelp_url):
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US;q=0.8,en;q=0.3",
        "Referer": "https://flippinpizza.com/",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "max-age=0",
    }

    r = session.get(yelp_url, headers=headers)
    tree = html.fromstring(r.text)
    text = "".join(
        tree.xpath("//script[contains(text(), 'regularHours')]/text()")
    ).replace("&quot;", '"')

    _tmp = []
    lines = text.split('"regularHours":')

    for l in lines:
        if l.find("dayOfWeekShort") == -1:
            continue

        time = l.split('["')[1].split('"]')[0]
        day = l.split('"dayOfWeekShort":"')[1].split('"')[0]
        _tmp.append(f"{day}: {time}")

    return ";".join(_tmp) or "<MISSING>"


def get_params():
    params = []
    session = SgRequests()
    r = session.get(
        "https://flippinpizza.com/wp-content/plugins/superstorefinder-wp/ssf-wp-xml.php"
    )
    tree = html.fromstring(r.content)
    items = tree.xpath("//item")
    for item in items:
        source = "".join(item.xpath("./description/text()"))
        root = html.fromstring(source)
        url = "".join(root.xpath("//div[@class='location-btn']/a/@href")).strip()
        lat = "".join(item.xpath("./latitude/text()")).strip() or "<MISSING>"
        lng = "".join(item.xpath("./longitude/text()")).strip() or "<MISSING>"
        params.append((url, (lat, lng)))

    return params


def get_data(params):
    page_url = params[0]
    latitude, longitude = params[1]
    locator_domain = "https://flippinpizza.com/"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    iscoming = "".join(tree.xpath("//title/text()")).lower()
    if "coming soon" in iscoming:
        return

    location_name = tree.xpath("//h1[@class='entry-title']/text()")[0].strip()
    line = tree.xpath("//h3[text()='Location Address']/following-sibling::p[1]/text()")
    line = list(filter(None, [l.strip() for l in line]))

    street_address = ", ".join(line[:-1]).strip()
    line = line[-1]
    city = line.split(",")[0].strip()
    line = line.split(",")[1].strip()
    state = line.split()[0]
    postal = line.split()[1]
    country_code = "US"
    store_number = "<MISSING>"
    phone = (
        "".join(tree.xpath("//p/a[contains(@href,'tel')]/text()")).strip()
        or "<MISSING>"
    )
    location_type = "<MISSING>"

    yelp_url = "".join(tree.xpath("//div[@class='hours-btn']/a/@href"))

    if yelp_url:
        hours_of_operation = get_hours(yelp_url)
    else:
        hours_of_operation = ";".join(
            tree.xpath(
                "//div[./strong[contains(text(), 'Hours')]]/following-sibling::div[./em]/em/text()"
            )
        )

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
    params = get_params()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, p): p for p in params}
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
