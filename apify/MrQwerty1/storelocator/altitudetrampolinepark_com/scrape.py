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
    urls = set()
    session = SgRequests()
    r = session.get("https://www.altitudetrampolinepark.com/locations/")
    tree = html.fromstring(r.text)
    uls = tree.xpath(
        "//div[@class='col-md-3']//ul[contains(@class, 'region list-unstyled')]"
    )

    for ul in uls:
        state = "".join(ul.xpath("./li/strong/text()")).strip()
        links = ul.xpath(".//li[@data-category='3' or @data-category='1']//text()")
        links = list(filter(None, [l.strip() for l in links]))

        for l in links:
            urls.add(
                f"https://www.altitudetrampolinepark.com/locations/?q={l}, {state}"
            )

    return urls


def get_hours(page_url):
    session = SgRequests()
    r = session.get(page_url)
    if r.status_code == 404:
        return "<MISSING>"

    tree = html.fromstring(r.text)
    li = tree.xpath("//h3[text()='Hours of Operation']/following-sibling::ul[1]/li")
    _tmp = []
    for l in li:
        day = " ".join("".join(l.xpath("./strong/text()")).split())
        time = "".join(l.xpath("./text()")).strip()
        _tmp.append(f"{day} {time}")

    return ";".join(_tmp) or "<MISSING>"


def get_data(url):
    rows = []
    locator_domain = "https://www.altitudetrampolinepark.com/"

    session = SgRequests()
    r = session.get(url)
    tree = html.fromstring(r.text)

    divs = tree.xpath("//div[contains(@class, 'dealer listing')]")

    for d in divs:
        page_url = "https://www.altitudetrampolinepark.com" + "".join(
            d.xpath("./@data-href")
        )
        location_name = "".join(d.xpath("./@data-name")).strip()
        line = d.xpath(".//li[@class='mt-1 text-white-50']//text()")
        line = list(filter(None, [l.strip() for l in line]))
        street_address = line[0]
        line = line[-1]
        city = line.split(",")[0].strip()
        line = line.split(",")[1].strip()
        state = line.split()[0]
        postal = line.split()[-1]
        country_code = "US"
        store_number = "".join(d.xpath("./@data-id")) or "<MISSING>"
        phone = (
            "".join(d.xpath(".//a[contains(@href, 'tel')]/text()")).strip()
            or "<MISSING>"
        )
        latitude = "".join(d.xpath("./@data-lat")) or "<MISSING>"
        longitude = "".join(d.xpath("./@data-lng")) or "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = get_hours(page_url)

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
    s = set()
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=1) as executor:
        future_to_url = {executor.submit(get_data, url): url for url in urls}
        for future in futures.as_completed(future_to_url):
            rows = future.result()
            for row in rows:
                _id = row[8]
                if _id not in s:
                    s.add(_id)
                    out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
