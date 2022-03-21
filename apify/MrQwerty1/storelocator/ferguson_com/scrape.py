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
    r = session.get("https://www.ferguson.com/searchBranch")
    tree = html.fromstring(r.text)

    return tree.xpath("//ul[@id='mapStates']/li/a/@title")


def get_data(url):
    rows = []
    coords = dict()
    locator_domain = "https://www.ferguson.com/"
    api = f"https://www.ferguson.com/branchResults?state={url}&distance=50"

    session = SgRequests()
    r = session.get(api)
    if api != r.url:
        return []

    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//div[@id='locations']/text()"))
    if text:
        js = json.loads(text)["locInfo"]
        for j in js:
            lat = j.get("latitude") or "<MISSING>"
            lng = j.get("longitude") or "<MISSING>"
            _id = j.get("warehouseId")
            coords[_id] = (lat, lng)

    divs = tree.xpath("//ul[@class='br-list']/li")
    for d in divs:
        line = d.xpath(".//div[@class='br-address-container']//text()")
        line = list(filter(None, [l.strip() for l in line]))
        if line[-1] == "United States":
            line.pop()

        street_address = ", ".join(line[:-1])
        line = line[-1]
        city = line.split(",")[0].strip()
        line = line.split(",")[1].strip()
        state = line.split()[0]
        postal = line.split()[1]
        country_code = "US"
        store_number = "".join(d.xpath("./@id")).replace("locationId", "")
        latitude, longitude = coords.get(store_number) or ("<MISSING>", "<MISSING>")

        cards = d.xpath(".//div[@class='br-item-card']")
        for c in cards:
            name = (
                "".join(d.xpath(".//p[@class='brli-title']/text()"))
                .split(".")[-1]
                .strip()
            )
            location_type = "".join(c.xpath("./a/text()")).strip()
            location_name = f"{name} - Ferguson {location_type}"
            phone = (
                "".join(c.xpath("./p[@class='phone-icon-box small']/text()")).strip()
                or "<MISSING>"
            )
            slug = "".join(c.xpath("./a/@href"))
            page_url = f"https://www.ferguson.com{slug}"

            _tmp = []
            hours = c.xpath(".//div[contains(@class,'store-day-hours')]")
            for h in hours:
                day = "".join(h.xpath("./p[1]//text()")).strip()
                time = "".join(h.xpath("./p[2]//text()")).strip()
                _tmp.append(f"{day}: {time}")

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
            rows.append(row)

    return rows


def fetch_data():
    out = []
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url): url for url in urls}
        for future in futures.as_completed(future_to_url):
            rows = future.result()
            out += rows

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
