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


def get_queries():
    queries = []
    session = SgRequests()
    r = session.get("https://elementsmassage.com/massage-places-near-me")
    tree = html.fromstring(r.text)
    urls = tree.xpath("//div[@class='container-fluid container-fluid-zero']//a/@href")
    for u in urls:
        q = u.split("=")[-1]
        queries.append(q)

    return queries


def get_url(query):
    session = SgRequests()
    r = session.get(
        f"https://api.mapbox.com/geocoding/v5/mapbox.places/{query}.json/?access_token=pk"
        f".eyJ1IjoicHRpbmRhbGwiLCJhIjoiY2ptYnphdmFrMDlxNDNwczRncG1pbnIyMSJ9.w4jiaYQ88OpNK6IaWPukXA"
        f"&country=US%2CCA&types=region%2Cpostcode%2Cplace"
    )
    js = r.json()["features"][0]

    q = js.get("place_name")
    lat = js.get("center")[1]
    lon = js.get("center")[0]
    url = f"https://elementsmassage.com/locator?q={q}&lat={lat}&lng={lon}"

    return url


def get_data(query):
    rows = []
    locator_domain = "https://elementsmassage.com/"
    api_url = get_url(query)

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()["locations"]

    for j in js:
        status = j.get("status")
        if status == "soon":
            continue
        page_url = f'https://elementsmassage.com/{j.get("slug")}'
        location_name = j.get("name").strip()
        street_address = (
            f"{j.get('address')} {j.get('address_2') or ''}".strip() or "<MISSING>"
        )
        city = j.get("city") or "<MISSING>"
        state = j.get("state") or "<MISSING>"
        postal = j.get("zip_code") or "<MISSING>"
        country = j.get("country") or "<MISSING>"
        if country == "United States":
            country_code = "US"
        else:
            country_code = "CA"

        store_number = j.get("id") or "<MISSING>"
        phone = j.get("phone_number") or "<MISSING>"
        latitude = j.get("latitude") or "<MISSING>"
        longitude = j.get("longitude") or "<MISSING>"
        location_type = "<MISSING>"

        _tmp = []
        hours = j.get("hours_of_operation", {}) or {}
        for k, v in hours.items():
            _tmp.append(f"{k}: {v}")

        hours_of_operation = "; ".join(_tmp) or "<MISSING>"

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
        rows.append(row)

    return rows


def fetch_data():
    out = []
    s = set()
    queries = get_queries()

    with futures.ThreadPoolExecutor(max_workers=2) as executor:
        future_to_url = {executor.submit(get_data, query): query for query in queries}
        for future in futures.as_completed(future_to_url):
            rows = future.result()
            for row in rows:
                _id = row[8]
                if _id not in s:
                    s.add(_id)
                    out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
