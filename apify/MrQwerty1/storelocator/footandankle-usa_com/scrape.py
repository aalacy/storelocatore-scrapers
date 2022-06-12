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
    _tmp = []
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    r = session.get(url, headers=headers)
    tree = html.fromstring(r.text)
    tr = tree.xpath("//tr[@itemprop='openingHours']")

    for t in tr:
        day = "".join(t.xpath("./td[1]//text()")).strip()
        time = "".join(t.xpath("./td[2]//text()")).strip()
        _tmp.append(f"{day}: {time}")

    return ";".join(_tmp) or "<MISSING>"


def fetch_data():
    out = []
    urls = []
    hours = dict()
    locator_domain = "https://www.footandankle-usa.com/"
    api_url = "https://www.footandankle-usa.com/wp-admin/admin-ajax.php?action=get_all_locations"

    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    r = session.get(api_url, headers=headers)
    js = r.json()

    for j in js:
        urls.append(j.get("link"))

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_hours, url): url for url in urls}
        for future in futures.as_completed(future_to_url):
            row = future.result()
            key = (
                future_to_url[future]
                .replace("https://www.footandankle-usa.com/", "")
                .replace("/", "-")
            )
            hours[key] = row

    for j in js:
        a = j.get("address")
        street_address = (
            f"{a.get('line1')} {a.get('line2') or ''}".strip() or "<MISSING>"
        )
        city = a.get("city") or "<MISSING>"
        state = a.get("state") or "<MISSING>"
        postal = a.get("zip") or "<MISSING>"
        country_code = "US"
        store_number = j.get("id")
        page_url = j.get("link")
        location_name = j.get("name")
        phone = j.get("phones", {}).get("telephone1") or "<MISSING>"
        latitude = a.get("lat") or "<MISSING>"
        longitude = a.get("lng") or "<MISSING>"
        location_type = "<MISSING>"
        key = page_url.replace("https://www.footandankle-usa.com/", "").replace(
            "/", "-"
        )
        hours_of_operation = hours.get(key)

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
