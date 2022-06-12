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


def get_params():
    params = []
    session = SgRequests()

    r = session.get("https://www.alamo.co.uk/en/car-hire-locations/gb.model.json")
    js = r.json()[":items"]["root"][":items"]["container_10"][":items"][
        "branch_locations_dra"
    ]["locations"]

    for j in js:
        adr = []
        url = j.get("url")
        lines = j.get("addressLines") or []
        for line in lines:
            if line.lower().find("enterprise") != -1:
                continue
            adr.append(line)

        params.append((url, ", ".join(adr)))

    return params


def get_data(params):
    session = SgRequests()
    url = params[0]
    street_address = params[1]
    locator_domain = "https://www.alamo.co.uk"
    page_url = f"{locator_domain}{url}"

    r = session.get(page_url)
    tree = html.fromstring(r.text)
    block = "".join(tree.xpath('//script[@id="mainschema"]/text()'))

    j = json.loads(block)
    a = j.get("address")
    state = a.get("addressRegion")
    city = a.get("addressLocality")
    postal = a.get("postalCode")
    country_code = a.get("addressCountry")
    store_number = "<MISSING>"
    location_name = j.get("name")
    phone = j.get("telephone")
    geo = j.get("geo")
    latitude = geo.get("latitude")
    longitude = geo.get("longitude")
    location_type = "<MISSING>"
    hours_of_operation = j.get("openingHours")

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
    params = get_params()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, param): param for param in params}
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
