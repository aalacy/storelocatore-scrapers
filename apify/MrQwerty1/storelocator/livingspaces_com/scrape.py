import csv
import json

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
    r = session.get("https://www.livingspaces.com/stores")
    tree = html.fromstring(r.text)
    return tree.xpath("//div[@class='st-detail']/a/@href")


def parse_html(tree, page_url):
    locator_domain = "https://www.livingspaces.com/"
    location_name = "".join(tree.xpath("//h1/text()")).strip()
    line = tree.xpath(
        "//div[@class='col-xs-5' and ./a[contains(@href, 'Map')]]/span/text()"
    )
    line = list(filter(None, [l.strip() for l in line]))
    street_address = ", ".join(line[:-1])
    line = line[-1]
    city = line.split(",")[0].strip()
    line = line.split(",")[1].strip()
    state = line.split()[0]
    postal = line.split()[1]
    country_code = "US"
    try:
        store_number = tree.xpath("//a[contains(@href, 'storeId=')]/@href")[0].split(
            "storeId="
        )[-1]
    except IndexError:
        store_number = "<MISSING>"

    phone = (
        "".join(tree.xpath("//div[@class='col-xs-3']/span/text()")).strip()
        or "<MISSING>"
    )
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    location_type = "<MISSING>"

    _tmp = []
    hours = tree.xpath(
        "//div[@class='col-xs-5' and ./span[contains(text(), 'Hours')]]/span"
    )
    for h in hours:
        if "".join(h.xpath("./text()")).lower().find("store hours") != -1:
            continue
        if "".join(h.xpath("./@class")):
            break
        _tmp.append("".join(h.xpath("./text()")).strip())

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


def get_data(url):
    locator_domain = "https://www.livingspaces.com/"
    page_url = f"https://www.livingspaces.com{url}"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[contains(text(),'FurnitureStore')]/text()"))
    if text:
        j = json.loads(text)
        location_name = "".join(tree.xpath("//h1/text()")).strip()
        a = j.get("address")
        street_address = a.get("streetAddress") or "<MISSING>"
        city = a.get("addressLocality") or "<MISSING>"
        state = a.get("addressRegion") or "<MISSING>"
        postal = a.get("postalCode") or "<MISSING>"

        if city == "Scottsdale":
            state = "AZ"
        country_code = "US"
        try:
            store_number = tree.xpath("//a[contains(@href, 'storeId=')]/@href")[
                0
            ].split("storeId=")[-1]
        except IndexError:
            store_number = "<MISSING>"
        phone = j.get("telephone") or "<MISSING>"
        g = j.get("geo")
        latitude = g.get("latitude") or "<MISSING>"
        longitude = g.get("longitude") or "<MISSING>"
        location_type = "<MISSING>"

        _tmp = []
        hours = j.get("openingHoursSpecification") or []
        for h in hours:
            days = h.get("dayOfWeek")
            if type(days) == list:
                day = f"{days[0]}-{days[-1]}"
            else:
                day = days
            start = h.get("opens")
            close = h.get("closes")
            _tmp.append(f"{day}: {start} - {close}")

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
    else:
        row = parse_html(tree, page_url)

    return row


def fetch_data():
    out = []
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=5) as executor:
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
