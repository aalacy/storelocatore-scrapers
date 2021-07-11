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
    r = session.get("https://locator.natwest.com/?")
    tree = html.fromstring(r.text)
    token = "".join(tree.xpath("//input[@id='csrf-token']/@value"))

    data = {
        "CSRFToken": token,
        "lat": "51.5073509",
        "lng": "-0.1277583",
        "site": "Natwest",
        "pageDepth": "4",
        "search_term": "London",
        "searchMiles": "100",
        "offSetMiles": "50",
        "maxMiles": "2000",
        "listSizeInNumbers": "10000",
        "search-type": "1",
    }

    r = session.post(
        "https://locator.natwest.com/content/branchlocator/en/natwest/_jcr_content/content/homepagesearch.search.html",
        data=data,
    )
    tree = html.fromstring(r.text)

    return tree.xpath(
        "//div[@class=' results-block real branch']/a[@class='holder']/@href"
    )


def get_data(url):
    locator_domain = "https://natwest.com"
    page_url = f"https://locator.natwest.com{url}"
    if "Mobile" in page_url:
        return

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//input[@id='branchName']/@value"))
    line = tree.xpath("//div[@class='print']//td[@class='first']/text()")
    line = list(filter(None, [l.strip() for l in line]))

    street_address = line[0]
    city = line[-3]
    state = line[-2]
    postal = line[-1]
    country_code = "GB"
    store_number = page_url.split("/")[-1].split("-")[0]

    phone = (
        "".join(tree.xpath("//div[@class='print']//td[./span]/text()")).strip()
        or "<MISSING>"
    )
    if phone.find("(") != -1:
        phone = phone.split("(")[0].strip()

    text = "".join(tree.xpath("//script[contains(text(), 'locationObject')]/text()"))
    text = text.split("locationObject =")[1].split(";")[0].strip()
    js = json.loads(text)
    latitude = js.get("LAT") or "<MISSING>"
    longitude = js.get("LNG") or "<MISSING>"
    location_type = js.get("TYPE") or "<MISSING>"

    _tmp = []
    tr = tree.xpath("//tr[@class='time']")

    for t in tr:
        day = "".join(t.xpath("./td[1]/text()")).strip()
        if t.xpath("./td[@colspan='3']"):
            time = "Closed"
        else:
            time = "".join(t.xpath("./td/text()")[1:]).strip()
        _tmp.append(f"{day}: {time}")

    hours_of_operation = ";".join(_tmp) or "<MISSING>"
    if hours_of_operation.lower().count("closed") >= 7:
        hours_of_operation = "Closed"

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
