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


def clean_phone(phone):
    _tmp = []
    for p in phone:
        if p.isdigit():
            _tmp.append(p)

    if len(_tmp) < 10:
        return "<MISSING>"

    return "".join(_tmp)


def get_hours(url):
    slug = url.split("/")[-1]
    session = SgRequests()
    try:
        r = session.get(url, timeout=10)
        tree = html.fromstring(r.text)

        _tmp = []
        li = tree.xpath("//ul[@class='hours-list']/li")
        for l in li:
            day = "".join(l.xpath("./span[1]/text()")).strip()
            time = "".join(l.xpath("./span[2]/text()")).strip()
            _tmp.append(f"{day}: {time}")

        hours = ";".join(_tmp) or "<MISSING>"
        if hours.find("Open 24") != -1:
            hours = hours.replace(":", "").strip()
    except:
        hours = "<MISSING>"

    return {slug: hours}


def fetch_data():
    out = []
    urls = []
    hours = []
    s = set()
    locator_domain = "https://memorialhermann.org/"

    headers = {
        "Connection": "keep-alive",
        "Accept": "application/json, text/plain, */*",
        "Authorization": "eyJhbGciOiJodHRwOi8vd3d3LnczLm9yZy8yMDAxLzA0L3htbGRzaWctbW9yZSNobWFjLXNoYTI1NiIsInR5cCI6IkpXVCJ9.eyJodHRwOi8vc2NoZW1hcy54bWxzb2FwLm9yZy93cy8yMDA1LzA1L2lkZW50aXR5L2NsYWltcy9uYW1lIjoiYWRtaW4iLCJleHAiOjIxMjcwNDQ1MTcsImlzcyI6Imh0dHBzOi8vZGV2ZWxvcGVyLmhlYWx0aHBvc3QuY29tIiwiYXVkIjoiaHR0cHM6Ly9kZXZlbG9wZXIuaGVhbHRocG9zdC5jb20ifQ.zNvR3WpI17CCMC7rIrHQCrnJg_6qGM21BvTP_ed_Hj8",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36 OPR/73.0.3856.284",
        "Content-Type": "application/json;charset=UTF-8",
    }

    data = '{"query":"","start":0,"rows":10000,"selectedFilters":{"distance":[20],"hasOnlineScheduling":false,"locationType":[],"lonlat":[-95.36,29.76],"service":[],"specialty":[]}}'
    session = SgRequests()
    r = session.post(
        "https://api.memorialhermann.org/api/locationsearch", headers=headers, data=data
    )
    js = r.json()["locations"]

    for j in js:
        urls.append("https://memorialhermann.org" + j.get("Url"))

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_hours, url): url for url in urls}
        for future in futures.as_completed(future_to_url):
            hours.append(future.result())

    hours = {k: v for elem in hours for (k, v) in elem.items()}

    for j in js:
        suite = j.get("Suite") or ""
        if suite:
            street_address = (
                f"{j.get('StreetNumber')} {j.get('StreetName')}, Suite {suite}".strip()
                or "<MISSING>"
            )
        else:
            street_address = (
                f"{j.get('StreetNumber')} {j.get('StreetName')}".strip() or "<MISSING>"
            )
        city = j.get("City") or "<MISSING>"
        state = j.get("State") or "<MISSING>"
        postal = j.get("PostalCode") or "<MISSING>"
        country_code = "US"
        store_number = "<MISSING>"
        page_url = f'https://memorialhermann.org{j.get("Url")}'
        location_name = j.get("Name")
        phone = j.get("Telephone") or "<MISSING>"
        phone = clean_phone(phone)
        loc = j.get("lonlat") or ["<MISSING>", "<MISSING>"]
        latitude = loc[1]
        longitude = loc[0]
        location_type = j.get("LocationType") or "<MISSING>"
        slug = page_url.split("/")[-1]
        hours_of_operation = hours.get(slug)

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

        check = tuple(row[2:8])
        if check not in s:
            s.add(check)
            out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
