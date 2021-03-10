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
    r = session.get(
        "https://maps.castrol.com/api/v1/client/search?countries=1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66&filters[]=16&lat=33.0218117&lng=-97.12516989999999"
    )
    js = r.json()["data"]
    for j in js:
        url = j.get("website_url", "") or ""
        if url.startswith("http://www.castrolpremiumlube.com/Store/"):
            urls.append(url)

    return urls


def get_data(page_url):
    locator_domain = "http://www.castrolpremiumlube.com"
    session = SgRequests()
    r = session.get(page_url)
    if len(r.text) == 0:
        return
    tree = html.fromstring(r.text)
    location_name = "".join(tree.xpath("//title/text()")).strip() or "<MISSING>"
    line = tree.xpath("//div[@class='address']/text()")
    line = list(filter(None, [l.strip() for l in line]))
    street_address = line[0]
    line = line[-1]
    city = line.split(",")[0].strip()
    line = line.split(",")[1].strip()
    state = line.split()[0].strip()
    postal = line.split()[1].strip()
    country_code = "US"
    store_number = location_name.split("#")[-1]
    phone = "".join(tree.xpath("//div[@class='phone']/text()")).strip() or "<MISSING>"
    if len(phone) > 14:
        phone = phone.split()[-1]
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    location_type = "<MISSING>"
    hours_of_operation = (
        ";".join(tree.xpath("//div[@class='hours']//td/div/text()")) or "<MISSING>"
    )
    if hours_of_operation.count("closed") == 7:
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
