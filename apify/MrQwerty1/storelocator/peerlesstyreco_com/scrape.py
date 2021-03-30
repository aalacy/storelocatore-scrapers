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
    r = session.get("https://peerlesstyreco.com/peerless-tires-store-locations/")
    tree = html.fromstring(r.text)

    return tree.xpath("//div[@class='btn-store-info']/a/@href")


def get_data(page_url):
    locator_domain = "https://peerlesstyreco.com/"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[contains(text(), 'apikey')]/text()"))
    key = text.split("'")[1]

    r = session.get(f"https://wl.tireconnect.ca/api/v2/location/list?key={key}")
    j = r.json()["data"]["locations"][0]

    location_name = j.get("name")
    street_address = (
        f'{j.get("address_line_1")} {j.get("address_line_2") or ""}'.strip()
        or "<MISSING>"
    )
    city = j.get("city") or "<MISSING>"
    state = j.get("province_code") or "<MISSING>"
    postal = j.get("postal_code") or "<MISSING>"
    country_code = j.get("country_code") or "<MISSING>"
    store_number = j.get("id") or "<MISSING>"
    phone = j.get("phone") or "<MISSING>"
    latitude = j.get("latitude") or "<MISSING>"
    longitude = j.get("longitude") or "<MISSING>"
    location_type = "<MISSING>"

    _tmp = []
    tr = tree.xpath(
        "//table[@class='table' and .//*[contains(text(), 'Hours')]]//tr[./td]"
    )

    for t in tr:
        day = "".join(t.xpath("./td[1]/text()")).strip()
        time = "".join(t.xpath("./td[2]/text()")).strip()
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
