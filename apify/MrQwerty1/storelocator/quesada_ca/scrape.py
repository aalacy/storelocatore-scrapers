import csv
import re

from concurrent import futures
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


def get_ids():
    session = SgRequests()
    r = session.get("https://locations.quesada.ca/")
    ids = re.findall(r'"id":(\d+)', r.text)

    return ids


def get_urls():
    urls = []

    ids = get_ids()
    batches = [ids[i : i + 20] for i in range(0, len(ids), 20)]
    for b in batches:
        url = f'https://sls-api-service.sweetiq-sls-production-west.sweetiq.com/eWhSvxJrhmw6w9pJkeeXCkK12mi4XC/locations-details?locale=en_CA&ids={",".join(b)}&cname=locations.quesada.ca'
        urls.append(url)

    return urls


def get_data(url):
    rows = []
    locator_domain = "https://quesada.ca/"

    session = SgRequests()
    r = session.get(url)
    js = r.json()["features"]

    for j in js:
        try:
            g = j.get("geometry").get("coordinates")
        except:
            g = ["<MISSING>", "<MISSING>"]

        j = j.get("properties")
        location_name = j.get("name")
        page_url = f'https://locations.quesada.ca/{j.get("slug")}'
        street_address = (
            f'{j.get("addressLine1")} {j.get("addressLine2") or ""}'.strip()
            or "<MISSING>"
        )
        city = j.get("city") or "<MISSING>"
        state = j.get("province") or "<MISSING>"
        postal = j.get("postalCode") or "<MISSING>"
        country_code = j.get("country") or "<MISSING>"
        store_number = "<MISSING>"
        phone = j.get("phoneLabel") or "<MISSING>"
        latitude = g[1]
        longitude = g[0]
        location_type = "<MISSING>"

        _tmp = []
        hours = j.get("hoursOfOperation") or {}
        for k, v in hours.items():
            _tmp.append(f'{k}: {"".join(map("-".join, v)) or "Closed"}')

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
        rows.append(row)

    return rows


def fetch_data():
    out = []
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url): url for url in urls}
        for future in futures.as_completed(future_to_url):
            rows = future.result()
            for row in rows:
                out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
