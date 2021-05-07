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
    r = session.get("https://www.randstadusa.com/locations/")
    tree = html.fromstring(r.text)

    return tree.xpath(
        "//div[@class='title card-title']/a[contains(@href, '/locations/')]/@href"
    )


def get_data(url):
    locator_domain = "https://www.randstadusa.com/"
    page_url = f"https://www.randstadusa.com{url}"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(
        tree.xpath("//div[@class='title card-title']/h2/text()")
    ).strip()
    line = tree.xpath("//div[@class='branch-info']//div[@class='address']/text()")
    line = list(filter(None, [l.strip() for l in line]))
    street_address = ", ".join(line[:-1]).replace("Remote Location", "") or "<MISSING>"
    line = line[-1]
    city = line.split(",")[0].strip()
    line = line.split(",")[1].strip()
    postal = line.split()[-1]
    state = line.replace(postal, "").strip()
    if not postal.isdigit():
        postal = "<MISSING>"
        state = line

    country_code = "US"
    store_number = page_url.split("_")[-1].replace("/", "")
    try:
        phone = tree.xpath("//div[@class='phone']//text()")[0].strip()
    except IndexError:
        phone = "<MISSING>"

    try:
        script = "".join(
            tree.xpath("//script[contains(text(), 'var jsonData')]/text()")
        )
        longitude, latitude = eval(
            script.split("jsonData ")[-1].split('"coordinates":')[1].split("},")[0]
        )
    except:
        latitude, longitude = "<MISSING>", "<MISSING>"
    location_type = "<MISSING>"

    _tmp = []
    hours = tree.xpath("//div[@id='collapse_hours']/div[@class='hours']")
    for h in hours:
        _tmp.append(" ".join(h.xpath(".//text()")))

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
    s = set()
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url): url for url in urls}
        for future in futures.as_completed(future_to_url):
            row = future.result()
            if row:
                check = tuple(row[2:7])
                if check not in s:
                    s.add(check)
                    out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
