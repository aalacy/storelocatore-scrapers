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


def get_ids():
    ids = []
    session = SgRequests()
    r = session.get(
        "https://www.pro-cuts.com/content/dam/sitemaps/pro-cuts/sitemap_pro-cuts_en_us.xml"
    )
    tree = html.fromstring(r.content)
    urls = tree.xpath("//loc[contains(text(), 'locations')]/text()")
    for u in urls:
        if u.find("-") != -1:
            u = u.split("-")[-1].replace(".html", "")
            if u.isdigit():
                ids.append(u)

    return ids


def get_data(_id):
    locator_domain = "https://www.pro-cuts.com/"
    api_url = f"https://info3.regiscorp.com/salonservices/siteid/3/salon/{_id}"

    session = SgRequests()
    r = session.get(api_url)
    j = r.json()

    location_name = j.get("name")
    street_address = j.get("address") or "<MISSING>"
    city = j.get("city") or "<MISSING>"
    state = j.get("state") or "<MISSING>"
    postal = j.get("zip") or "<MISSING>"
    country_code = "US"
    store_number = j.get("storeID") or "<MISSING>"
    phone = j.get("phonenumber") or "<MISSING>"
    latitude = j.get("latitude") or "<MISSING>"
    longitude = j.get("longitude") or "<MISSING>"
    page_url = f'https://www.pro-cuts.com/locations/{state.lower()}/{city.lower().replace(" ", "-")}/{location_name.lower().replace("-", "").replace(" ", "-")}-haircuts-{store_number}.html'
    location_type = "<MISSING>"

    _tmp = []
    hours = j.get("store_hours") or []
    for h in hours:
        day = h.get("days")
        start = h.get("hours").get("open")
        close = h.get("hours").get("close")
        if start:
            _tmp.append(f"{day}: {start} - {close}")
        else:
            _tmp.append(f"{day}: Closed")

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

    return row


def fetch_data():
    out = []
    ids = get_ids()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, _id): _id for _id in ids}
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
