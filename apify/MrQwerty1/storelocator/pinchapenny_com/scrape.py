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
    hours = tree.xpath("//time[@itemprop='openingHours']")
    for h in hours:
        day = "".join(h.xpath("./strong/text()")).strip()
        time = "".join(h.xpath("./text()")).strip()
        _tmp.append(f"{day} {time}")

    hoo = ";".join(_tmp) or "Coming Soon"
    return {_id: hoo}


def fetch_data():
    out = []
    hours = []
    urls = []
    url = "https://pinchapenny.com/"
    api_url = "https://pinchapenny.com/api/store/search?lat=49.588299&lng=34.551399"

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()["data"]
    for j in js:
        urls.append(j.get("url"))

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_hours, url): url for url in urls}
        for future in futures.as_completed(future_to_url):
            hours.append(future.result())

    hours = {k: v for element in hours for k, v in element.items()}

    for j in js:
        locator_domain = url
        location_name = j.get("name") or "<MISSING>"
        street_address = (
            f"{j.get('address')} {j.get('address_extended') or ''}".strip()
            or "<MISSING>"
        )
        city = j.get("locality") or "<MISSING>"
        state = j.get("region") or "<MISSING>"
        postal = j.get("postcode") or "<MISSING>"
        country_code = "US"
        store_number = j.get("corporate_id") or "<MISSING>"
        page_url = j.get("url") or "<MISSING>"
        phone = j.get("phone") or "<MISSING>"
        latitude = j.get("latitude") or "<MISSING>"
        longitude = j.get("longitude") or "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = hours.get(store_number)

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
