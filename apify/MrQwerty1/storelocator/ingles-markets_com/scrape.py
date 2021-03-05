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


def get_input(state):
    lines = []
    session = SgRequests()
    url = f"https://www.ingles-markets.com/storelocate/storelocator.php?address={state}"
    r = session.get(url)
    tree = html.fromstring(r.content)
    markers = tree.xpath("//marker")
    for m in markers:
        _tmp = {
            "store_number": "".join(m.xpath("./@id")),
            "location_name": "".join(m.xpath("./@name")),
            "city": "".join(m.xpath("./@city")),
            "state": "".join(m.xpath("./@state")),
            "street_address": "".join(m.xpath("./@address")),
            "lat": "".join(m.xpath("./@lat")),
            "lon": "".join(m.xpath("./@lng")),
        }
        lines.append(_tmp)

    return lines


def get_data(line):
    locator_domain = "https://www.ingles-markets.com/"
    _id = line.get("store_number")
    page_url = (
        f"https://www.ingles-markets.com/storelocate/storeinfo.php?storenum={_id}"
    )

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = f"Ingles Markets #{_id}"
    street_address = line.get("street_address").strip()
    city = line.get("city") or "<MISSING>"
    state = line.get("state") or "<MISSING>"
    postal_text = "".join(tree.xpath(f"//strong[contains(text(), '{city}')]/text()"))
    try:
        postal = postal_text.split(".")[-1].strip()
    except IndexError:
        postal = "<MISSING>"
    country_code = "US"
    store_number = _id
    try:
        phone = tree.xpath("//a[contains(@href, 'tel')]/text()")[0]
    except IndexError:
        phone = "<MISSING>"
    latitude = line.get("lat") or "<MISSING>"
    longitude = line.get("lon") or "<MISSING>"
    location_type = "<MISSING>"

    text = tree.xpath("//div[@align='center']//text()")
    try:
        hours_of_operation = (
            ";".join(text[text.index("Store Hours:") + 1 : text.index("Store Phone: ")])
            or "<MISSING>"
        )
    except:
        hours_of_operation = "<MISSING>"

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
    inputs = []
    states = [
        "AL",
        "AK",
        "AZ",
        "AR",
        "CA",
        "CO",
        "CT",
        "DC",
        "DE",
        "FL",
        "GA",
        "HI",
        "ID",
        "IL",
        "IN",
        "IA",
        "KS",
        "KY",
        "LA",
        "ME",
        "MD",
        "MA",
        "MI",
        "MN",
        "MS",
        "MO",
        "MT",
        "NE",
        "NV",
        "NH",
        "NJ",
        "NM",
        "NY",
        "NC",
        "ND",
        "OH",
        "OK",
        "OR",
        "PA",
        "RI",
        "SC",
        "SD",
        "TN",
        "TX",
        "UT",
        "VT",
        "VA",
        "WA",
        "WV",
        "WI",
        "WY",
    ]

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_input, state): state for state in states}
        for future in futures.as_completed(future_to_url):
            lines = future.result()
            for line in lines:
                inputs.append(line)

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, inp): inp for inp in inputs}
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
