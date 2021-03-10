import csv
import re

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
    _id = url.split("/")[-1]
    session = SgRequests()
    r = session.get(url)
    tree = html.fromstring(r.text)

    _tmp = []
    hours = tree.xpath("//div[@class='footer_block']/img/following-sibling::p")
    days = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
    for h in hours[-1].xpath(".//text()"):
        for d in days:
            if h.find(d) != -1:
                if h.find("|") != -1:
                    h = h.split("|")[0].strip()
                if h.find("pick up,") != -1:
                    h = h.split("pick up,")[-1].strip()
                _tmp.append(h.strip())
                break

    v = ";".join(_tmp) or "<MISSING>"
    return {_id: v}


def fetch_data():
    out = []
    urls = []
    hours = []
    session = SgRequests()
    locator_domain = "https://www.signsbytomorrow.com/"
    data = {"searchaddress": "75022", "r": "5000"}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0",
        "Accept": "*/*",
        "Accept-Language": "uk-UA,uk;q=0.8,en-US;q=0.5,en;q=0.3",
        "Referer": "https://www.signsbytomorrow.com/storelocator",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://www.signsbytomorrow.com",
        "Connection": "keep-alive",
        "TE": "Trailers",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }

    r = session.post(
        "https://www.signsbytomorrow.com/cms/findcenter/search_locations.aspx",
        data=data,
        headers=headers,
    )
    text = r.text
    t = re.sub(
        r"([{,:])(\w+)([},:])",
        '\\1"\\2"\\3',
        text.split("locations:")[1].replace("})", ""),
    )
    js = eval(t)

    for j in js:
        urls.append(j.get("fr_directory"))

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_hours, url): url for url in urls}
        for future in futures.as_completed(future_to_url):
            hours.append(future.result())

    hours = {k: v for elem in hours for (k, v) in elem.items()}

    for j in js:
        page_url = j.get("fr_directory")
        _id = page_url.split("/")[-1]
        location_name = j.get("fr_name")
        street_address = f'{j.get("ad1")} {j.get("ad2") or ""}'.strip() or "<MISSING>"
        city = j.get("city") or "<MISSING>"
        state = j.get("state") or "<MISSING>"
        postal = j.get("zip") or "<MISSING>"
        country_code = "US"
        store_number = j.get("fr_id") or "<MISSING>"
        phone = j.get("tel") or "<MISSING>"

        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lon") or "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = hours.get(_id)

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
