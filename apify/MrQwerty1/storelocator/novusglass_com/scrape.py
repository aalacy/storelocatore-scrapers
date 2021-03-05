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
    urls = []
    session = SgRequests()
    start = [
        "https://novusglass.com/us/en/all-locations/?us=yes",
        "https://novusglass.com/us/en/all-locations/?canada=yes",
    ]

    for s in start:
        r = session.get(s)
        tree = html.fromstring(r.text)
        urls += tree.xpath(
            "//div[contains(@class,'letter letter')]/following-sibling::a/@href"
        )

    return urls


def get_data(page_url):
    locator_domain = "https://novusglass.com/"
    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = " ".join(" ".join(tree.xpath("//h1//text()")).split())
    line = tree.xpath("//div[@class='address']/text()")
    line = list(filter(None, [l.strip() for l in line]))
    if line:
        street_address = " ".join(" ".join(line[:-1]).split())
        line = line[-1].strip()
        try:
            city = line.split(",")[0].strip() or "<MISSING>"
            line = line.split(",")[1].strip()
            if line.lower().find("pei ") != -1:
                state = line[:3].strip()
                postal = line[3:].strip()
            else:
                state = line[:2].strip() or "<MISSING>"
                postal = line[2:].strip() or "<MISSING>"
        except:
            city = "<MISSING>"
            state = line.split()[0].strip()
            postal = line.replace(state, "").strip() or "<MISSING>"

        if len(postal) == 5:
            country_code = "US"
        else:
            country_code = "CA"

        if state == "Sorel":
            city = state
            state = "<MISSING>"
    else:
        street_address = "<MISSING>"
        city = "<MISSING>"
        state = "<MISSING>"
        postal = "<MISSING>"
        country_code = "<MISSING>"
    store_number = "<MISSING>"
    phone = "".join(
        tree.xpath("//div[@class='phone']//span[not(@class)]/text()")
    ).strip()

    script = "".join(
        tree.xpath("//script[contains(text(), 'new google.maps.LatLng')]/text()")
    )
    try:
        latitude = script.split("LatLng(")[1].split(",")[0]
        longitude = script.split("LatLng(")[1].split(",")[1].split(")")[0]
    except:
        latitude = "<MISSING>"
        longitude = "<MISSING>"
    location_type = "<MISSING>"

    _tmp = []
    tr = tree.xpath("//div[@class='business-hours']//tr")
    for t in tr:
        _tmp.append(" ".join(t.xpath("./td/text()")))

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
