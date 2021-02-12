import csv
import datetime
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


def get_map_from_google_url(url):
    try:
        if url.find("ll=") != -1:
            latitude = url.split("ll=")[1].split(",")[0]
            longitude = url.split("ll=")[1].split(",")[1].split("&")[0]
        else:
            latitude = url.split("@")[1].split(",")[0]
            longitude = url.split("@")[1].split(",")[1]
    except IndexError:
        latitude, longitude = "<MISSING>", "<MISSING>"

    return latitude, longitude


def get_hoo(slug):
    _tmp = []
    session = SgRequests()
    for x in range(7):
        date = datetime.date.today() + datetime.timedelta(days=x)
        day = date.strftime("%Y-%m-%d")
        url = f"https://www.greatwolf.com/5b27c1ed2bb0ac3618d7cc55/www.greatwolf.com/v~4b.15f/content/gw-www/php-root/{slug}/en/jcr:content/root/responsivegrid_327483370/waterpark_hours.json?date={day}&wph=true"
        weekday = date.strftime("%A")
        r = session.get(url)
        try:
            js = r.json()["eventList"][0]
            start = js.get("startTime")
            close = js.get("endTime")
            _tmp.append(f"{weekday}: {start} - {close}")
        except:
            pass

    return ";".join(_tmp).replace(":00 ", " ") or "<MISSING>"


def get_urls():
    session = SgRequests()
    r = session.get("https://www.greatwolf.com/")
    tree = html.fromstring(r.text)

    return tree.xpath("//li[contains(@class, 'open')]/a/@href")


def get_data(url):
    locator_domain = "https://www.greatwolf.com/"
    page_url = f"https://www.greatwolf.com{url}"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    text = "".join(
        tree.xpath("//script[contains(text(), '{}')]/text()".format('"address":'))
    )
    j = json.loads(text)

    location_name = j.get("name")
    a = j.get("address") or {}
    street_address = a.get("streetAddress") or "<MISSING>"
    city = a.get("addressLocality") or "<MISSING>"
    state = a.get("addressRegion") or "<MISSING>"
    postal = a.get("postalCode") or "<MISSING>"
    country_code = "US"
    if len(postal) > 5:
        country_code = "CA"
    store_number = "<MISSING>"
    phone = j.get("telephone") or "<MISSING>"
    _map = j.get("hasMap") or ""
    latitude, longitude = get_map_from_google_url(_map)
    location_type = "<MISSING>"
    hours_of_operation = get_hoo(url.replace("/", ""))

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
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url): url for url in urls}
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
