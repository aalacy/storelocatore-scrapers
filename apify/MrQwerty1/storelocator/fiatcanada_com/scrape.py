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


def get_hours(code):
    _tmp = []
    session = SgRequests()
    url = f"https://www.fiatcanada.com/en/dealers/{code}"
    r = session.get(url)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@id='sales-tab']//p[@class='C_DD-week-day']")
    for d in divs:
        day = "".join(d.xpath("./span[1]/text()")).strip()
        time = "".join(d.xpath("./span[last()]/text()")).strip()
        _tmp.append(f"{day}: {time}")

    return ";".join(_tmp) or "<MISSING>"


def fetch_data():
    out = []
    codes = []
    hours = dict()
    s = set()
    locator_domain = "https://www.fiatcanada.com/"
    api_url = "https://www.fiatcanada.com/data/dealers/expandable-radius?brand=fiat&longitude=-79.3984&latitude=43.7068&radius=5000"

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()["dealers"]

    for j in js:
        codes.append(j.get("code"))

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_hours, code): code for code in codes}
        for future in futures.as_completed(future_to_url):
            time = future.result()
            code = future_to_url[future]
            hours[code] = time

    for j in js:
        street_address = j.get("address") or "<MISSING>"
        city = j.get("city") or "<MISSING>"
        state = j.get("province") or "<MISSING>"
        postal = j.get("zipPostal") or "<MISSING>"
        country_code = "CA"
        store_number = j.get("code") or "<MISSING>"
        page_url = f"https://www.fiatcanada.com/en/dealers/{store_number}"
        location_name = j.get("name")
        phone = j.get("contactNumber") or "<MISSING>"
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

        if store_number not in s:
            out.append(row)
            s.add(store_number)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
