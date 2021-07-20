import csv
from lxml import html
from sgrequests import SgRequests
from sgzip.static import static_coordinate_list, SearchableCountries

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Accept": "*/*",
    "Accept-Language": "uk-UA,uk;q=0.8,en-US;q=0.5,en;q=0.3",
    "X-Requested-With": "XMLHttpRequest",
    "Alt-Used": "www.udfinc.com",
    "Connection": "keep-alive",
    "Referer": "https://www.udfinc.com/our-stores/",
    "TE": "Trailers",
}


def get_data(coord):
    rows = []
    lat, lon = coord
    locator_domain = "https://www.udfinc.com/"
    api_url = f"https://www.udfinc.com/wp-admin/admin-ajax.php?action=store_search&lat={lat}&lng={lon}&max_results=100&search_radius=200"

    session = SgRequests()
    r = session.get(api_url, headers=headers)
    try:
        js = r.json()
    except:
        js = []

    for j in js:
        page_url = j.get("permalink") or "<MISSING>"
        location_name = j.get("store").replace("&#038;", "").strip()
        street_address = (
            f"{j.get('address')} {j.get('address2') or ''}".strip() or "<MISSING>"
        )
        city = j.get("city") or "<MISSING>"
        state = j.get("state") or "<MISSING>"
        postal = j.get("zip") or "<MISSING>"
        country_code = "US"
        store_number = j.get("store_number") or "<MISSING>"
        phone = j.get("phone") or "<MISSING>"
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
        location_type = "<MISSING>"

        _tmp = []
        hours = j.get("hours") or "<html></html>"
        tree = html.fromstring(hours)
        tr = tree.xpath("//tr")

        for t in tr:
            day = "".join(t.xpath("./td/text()"))
            time = "".join(t.xpath(".//time/text()"))
            _tmp.append(f"{day}: {time}")

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
    data = []
    raw = []
    ids = []

    coords = static_coordinate_list(radius=200, country_code=SearchableCountries.USA)
    for coord in coords:
        raw.append(get_data(coord))

    for row in raw:
        if row == []:
            continue
        for location in row:
            if location[8] not in ids:
                ids.append(location[8])
                data.append(location)

    return data


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


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
