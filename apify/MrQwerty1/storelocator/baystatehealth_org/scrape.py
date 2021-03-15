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


def clean_phone(line):
    if "," in line:
        line = line.split(",")[0].strip()

    if "(" in line:
        _tmp = []
        for l in line:
            if l.isdigit() and len(_tmp) != 10:
                _tmp.append(l)

        if len(_tmp) < 10:
            return "<MISSING>"

        _tmp.insert(3, "-")
        _tmp.insert(7, "-")
        line = "".join(_tmp)

    return line


def clean_hours(line):
    line = line.replace("Main Clinic Facility:;300 Birnie Avenue Springfield, MA;", "")
    splitters = [
        "(",
        "We ",
        "Holidays",
        "Times",
        "*",
        "Patient",
        "Open for",
        "Ultrasound",
        "Screenings",
        "Xray",
        "Physical",
    ]
    for s in splitters:
        if s in line:
            line = line.split(s)[0].strip()

    return line


def get_params():
    _types = dict()
    coords = dict()
    session = SgRequests()
    r = session.get("https://www.baystatehealth.org/locations")
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[contains(text(),'var maplocations=')]/text()"))
    js = json.loads(text.split("var maplocations=")[1])

    for _type, records in js.items():
        for record in records:
            slug = record.get("LocationDetailLink")
            if _types.get(slug) is None:
                _types[slug] = _type
            else:
                _types[slug] = f"{_types[slug]}, {_type}"
            lat = record.get("LocationLat") or "<MISSING>"
            lng = record.get("LocationLon") or "<MISSING>"
            coords[slug] = (lat, lng)
    return _types, coords


def get_urls():
    urls = []
    session = SgRequests()
    for i in range(1, 5000):
        r = session.get(
            f"https://www.baystatehealth.org/locations/search-results?page={i}"
        )
        tree = html.fromstring(r.text)
        links = tree.xpath(
            "//a[contains(@id, 'main_1_contentpanel_1_lvSearchResults_hlItem_')]/@href"
        )
        urls += links

        if len(links) < 10:
            break

    return urls


def get_data(url, _types, coords):
    locator_domain = "https://www.baystatehealth.org/"
    page_url = f"https://www.baystatehealth.org{url}"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//h1/span/text()")).strip()
    street_address = (
        ", ".join(
            tree.xpath("//span[contains(@class, 'location-address')]/text()")
        ).strip()
        or "<MISSING>"
    )
    city = (
        "".join(tree.xpath("//span[@class='location-town']/text()")).strip()
        or "<MISSING>"
    )
    state = (
        "".join(tree.xpath("//span[@class='location-state']/text()")).strip()
        or "<MISSING>"
    )
    postal = (
        "".join(tree.xpath("//span[@class='location-zip']/text()")).strip()
        or "<MISSING>"
    )
    country_code = "US"
    store_number = "<MISSING>"
    phone = (
        "".join(tree.xpath("//span[@class='location-office-phone']/a/text()")).strip()
        or "<MISSING>"
    )
    if phone != "<MISSING>":
        phone = clean_phone(phone)
    else:
        phone = (
            "".join(
                tree.xpath("//span[@class='location-office-appointment-phone']/text()")
            ).strip()
            or "<MISSING>"
        )
    latitude, longitude = coords.get(url) or ("<MISSING>", "<MISSING>")
    if latitude == "<MISSING>":
        for k in coords.keys():
            if k in url:
                latitude, longitude = coords[k]
                break
    location_type = _types.get(url) or "<MISSING>"
    hours = tree.xpath("//div[@id='main_2_contentpanel_1_pnlOfficeHours']//text()")
    hours = list(filter(None, [h.strip() for h in hours]))

    if hours:
        hours_of_operation = clean_hours(";".join(hours)) or "<MISSING>"
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
    urls = get_urls()
    _types, coords = get_params()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {
            executor.submit(get_data, url, _types, coords): url for url in urls
        }
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
