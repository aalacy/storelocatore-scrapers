import csv
import html as h

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
    data = {"state": state}
    session = SgRequests()
    r = session.post("https://insomniacookies.com/locations/searchStores", data=data)
    js = r.json()["stores"]
    for j in js:
        j = j.get("store_info")
        _tmp = {
            "store_number": j.get("id") or "<MISSING>",
            "location_name": j.get("name") or "<MISSING>",
            "city": j.get("city") or "<MISSING>",
            "state": j.get("state") or "<MISSING>",
            "postal": j.get("zip") or "<MISSING>",
            "street_address": j.get("address") or "<MISSING>",
            "country": "US",
            "lat": j.get("store_lat") or "<MISSING>",
            "lon": j.get("store_lon") or "<MISSING>",
            "phone": j.get("phone") or "<MISSING>",
            "locator_domain": "https://insomniacookies.com/",
            "page_url": f"https://insomniacookies.com/locations/store/{j.get('id')}/ajax?",
            "location_type": "<MISSING>",
        }
        lines.append(_tmp)

    return lines


def get_data(line):
    session = SgRequests()

    page_url = line.get("page_url")
    r = session.get(page_url)
    text = r.json()["html"]
    tree = html.fromstring(h.unescape(text))

    _tmp = []
    tr = tree.xpath("//table")[0].xpath("//tr")
    a = False
    for t in tr:
        day = "".join(t.xpath("./td[1]/text()")).strip()
        if day == "Sunday" and a:
            break
        if day == "Sunday" and not a:
            a = True
        time = "".join(t.xpath("./td[2]/text()")).strip()
        _tmp.append(f"{day}: {time}")

    hours_of_operation = ";".join(_tmp) or "<MISSING>"

    row = [
        line.get("locator_domain"),
        line.get("page_url").replace("/ajax?", ""),
        line.get("location_name"),
        line.get("street_address"),
        line.get("city"),
        line.get("state"),
        line.get("postal"),
        line.get("country"),
        line.get("store_number"),
        line.get("phone"),
        line.get("location_type"),
        line.get("lat"),
        line.get("lon"),
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
