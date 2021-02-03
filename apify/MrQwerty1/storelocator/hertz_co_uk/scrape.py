import csv

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


def get_urls():
    urls = []
    session = SgRequests()
    r = session.get("https://api.hertz.com/rest/geography/city/country/GB?dialect=enGB")
    js = r.json()["data"]["model"]
    for j in js:
        u = f'https://api.hertz.com/rest/location/country/GB/city/{j.get("name")}?dialect=enGB'
        urls.append(u)

    return urls


def get_data(url):
    rows = []
    locator_domain = "https://www.hertz.co.uk/"

    session = SgRequests()
    r = session.get(url)
    js = r.json()["data"]["locations"]

    for j in js:
        location_name = j.get("locationName")
        street_address = (
            f'{j.get("streetAddressLine1")} {j.get("streetAddressLine2") or ""}'.strip()
            or "<MISSING>"
        )
        city = j.get("city") or "<MISSING>"
        state = j.get("state") or "<MISSING>"
        postal = j.get("zip") or "<MISSING>"
        country_code = j.get("countryCode") or "<MISSING>"
        slug = j.get("extendedOAGCode")
        page_url = f"https://www.hertz.co.uk/rentacar/location/united%20kingdom/{city.lower()}/{slug}?origin=Homepage"
        store_number = "<MISSING>"
        phone = j.get("phoneNumber").replace("*", "").strip() or "<MISSING>"
        latitude = j.get("latitude") or "<MISSING>"
        longitude = j.get("longitude") or "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = j.get("hours") or "<MISSING>"

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
