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


def get_hours(slug):
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    }
    url = f"https://www.usstoragecenters.com{slug}"
    r = session.get(url, headers=headers)
    tree = html.fromstring(r.text)

    _tmp = []
    li = tree.xpath("//div[@class='ww-location-d__office_hours']//li")
    for l in li:
        day = "".join(l.xpath("./span[1]//text()")).strip()
        time = "".join(l.xpath("./span[2]//text()")).strip()
        _tmp.append(f"{day}: {time}")

    return ";".join(_tmp) or "<MISSING>"


def fetch_data():
    out = []
    urls = []
    hours = {}
    locator_domain = "https://www.usstoragecenters.com/"
    api_url = "https://www.usstoragecenters.com/storage-units/?spa=true"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    }

    session = SgRequests()
    r = session.get(api_url, headers=headers)
    js = r.json()["data"]["content"][0]["context"]["items"]

    for j in js:
        urls.append(j.get("url"))

    with futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_url = {executor.submit(get_hours, url): url for url in urls}
        for future in futures.as_completed(future_to_url):
            val = future.result()
            key = future_to_url[future]
            hours[key] = val

    for j in js:
        a = j.get("address")
        street_address = a.get("address") or "<MISSING>"
        city = a.get("city") or "<MISSING>"
        state = a.get("state") or "<MISSING>"
        postal = a.get("zip") or "<MISSING>"
        country_code = "US"
        store_number = j.get("locationCode") or "<MISSING>"
        slug = j.get("url")
        page_url = f"https://www.usstoragecenters.com{slug}"
        location_name = j.get("sanitizedHeader") or "US Storage Centers"
        try:
            phone = j["phone"]["label"]["value"]
        except TypeError:
            phone = "<MISSING>"
        latitude = a.get("latitude") or "<MISSING>"
        longitude = a.get("longitude") or "<MISSING>"
        if "°" in latitude or "°" in longitude:
            latitude = (
                latitude.replace(".", "")
                .replace("'", "")
                .replace('"', "")
                .replace("N", "")
                .replace("°", ".")
            )
            longitude = "-" + longitude.replace(".", "").replace("'", "").replace(
                '"', ""
            ).replace("W", "").replace("°", ".")
        location_type = "<MISSING>"
        hours_of_operation = hours.get(slug) or "<MISSING>"

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
