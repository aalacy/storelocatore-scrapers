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


def get_hours(url):
    _id = url.split("-")[-1]
    session = SgRequests()
    r = session.get(url)
    tree = html.fromstring(r.text)

    _tmp = []
    hours = tree.xpath("//div[text()='Hours']/following-sibling::div[1]/p/text()")
    for h in hours:
        if h.find("Senior") != -1:
            break
        _tmp.append(h.strip())

    return {_id: ";".join(_tmp)}


def fetch_data():
    out = []
    urls = []
    hours = []
    session = SgRequests()
    locator_domain = "https://www.shopmarketbasket.com/"
    r = session.get("https://www.shopmarketbasket.com/store-locations-rest")
    js = r.json()

    for j in js:
        urls.append("https://www.shopmarketbasket.com" + j.get("path"))

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_hours, url): url for url in urls}
        for future in futures.as_completed(future_to_url):
            hours.append(future.result())

    hours = {k: v for elem in hours for (k, v) in elem.items()}

    for j in js:
        page_url = "https://www.shopmarketbasket.com" + j.get("path")
        _id = page_url.split("-")[-1]
        location_name = j.get("title")
        street_address = (
            f'{j.get("field_address_address_line1")} {j.get("field_address_address_line2") or ""}'.strip()
            or "<MISSING>"
        )
        city = j.get("field_address_locality") or "<MISSING>"
        state = j.get("field_address_administrative_area") or "<MISSING>"
        postal = j.get("field_address_postal_code") or "<MISSING>"
        country_code = "US"
        if _id.isdigit():
            store_number = _id
        else:
            store_number = "<MISSING>"
        phone = j.get("field_phone_number") or "<MISSING>"

        latitude, longitude = j.get("field_geolocation").split(",") or [
            "<MISSING>",
            "<MISSING>",
        ]
        location_type = "<MISSING>"
        hours_of_operation = hours.get(_id)

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

        out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
