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
    r = session.get("https://fmtrust.bank/locations-atms/")
    tree = html.fromstring(r.text)

    return tree.xpath("//div[@class='cell']/a/@href")


def get_data(url):
    rows = []
    locator_domain = "https://fmtrust.bank/"
    page_url = f"https://fmtrust.bank{url}"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@class='grid-x grid-padding-x location-component']")

    for d in divs:
        location_name = "".join(d.xpath(".//h3/text()")).strip()
        line = d.xpath(".//h3/following-sibling::p[1]/text()")
        line = list(filter(None, [l.strip() for l in line]))

        street_address = line[0]
        line = line[1]
        city = line.split(",")[0].strip()
        line = line.split(",")[1].strip()
        state = line.split()[0]
        postal = line.split()[1]
        country_code = "US"
        store_number = "<MISSING>"
        phone = (
            "".join(d.xpath(".//a[contains(@href, 'tel')]/text()")).strip()
            or "<MISSING>"
        )
        latitude = "".join(tree.xpath("//div[@data-lat]/@data-lat")) or "<MISSING>"
        longitude = "".join(tree.xpath("//div[@data-lat]/@data-lng")) or "<MISSING>"
        location_type = "<MISSING>"

        _tmp = []
        tr = d.xpath(".//div[@class='grid-x']//tr[./td]")
        for t in tr:
            day = "".join(t.xpath("./td[1]/text()")).strip()
            time = "".join(t.xpath("./td[2]//text()")).strip()
            _tmp.append(f"{day}: {time}")
            if day == "Sunday":
                break

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
            for row in rows:
                out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
