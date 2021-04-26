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
    coords = dict()
    ids = []
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0"
    }
    r = session.get(
        "https://paciugo.com/wp-content/themes/paciugo/inc/store-locator/phpsqlsearch_genxml.php",
        headers=headers,
    )
    tree = html.fromstring(r.content)
    markers = tree.xpath("//marker")
    for m in markers:
        _id = "".join(m.xpath("./@storeid"))
        lat = "".join(m.xpath("./@lat")) or "<MISSING>"
        lng = "".join(m.xpath("./@lng")) or "<MISSING>"
        coords[_id] = (lat, lng)
        ids.append(_id)

    return coords, ids


def get_data(_id, coords):
    locator_domain = "https://paciugo.com/"
    page_url = "https://paciugo.com/store-locator/"
    data = {"action": "ajaxretrievestorebyid", "storeID": _id}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "uk-UA,uk;q=0.8,en-US;q=0.5,en;q=0.3",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://paciugo.com",
        "Connection": "keep-alive",
        "Referer": "https://paciugo.com/store-locator/",
        "TE": "Trailers",
    }
    session = SgRequests()
    r = session.post(
        "https://paciugo.com/wp-admin/admin-ajax.php", data=data, headers=headers
    )
    tree = html.fromstring(r.json()["message"].replace("\u201d", ""))
    location_name = "".join(tree.xpath("//h3[@itemprop='name']/text()")).strip()
    adr1 = "".join(tree.xpath("//span[@itemprop='streetAddress']/text()")).strip()
    if "TX" in adr1:
        adr1 = adr1.split(",")[0]
    adr2 = "".join(tree.xpath("//span[@class='suite']/text()")).strip()
    street_address = f"{adr1} {adr2}".strip() or "<MISSING>"
    city = "".join(tree.xpath("//span[@itemprop='addressLocality']/text()")).strip()
    state = "".join(tree.xpath("//span[@itemprop='addressRegion']/text()")).strip()
    postal = "".join(tree.xpath("//span[@itemprop='postalCode']/text()")).strip()
    country_code = "US"
    store_number = _id
    phone = (
        "".join(tree.xpath("//span[@itemprop='telephone']/text()")).strip()
        or "<MISSING>"
    )
    latitude, longitude = coords[_id]
    location_type = "<MISSING>"

    _tmp = []
    days = tree.xpath("//div[@class='days-of-week']/text()")
    times = tree.xpath("//div[@class='hours']/text()")

    for d, t in zip(days, times):
        _tmp.append(f"{d.strip()} {t.strip()}")

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
    coords, ids = get_ids()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, _id, coords): _id for _id in ids}
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
