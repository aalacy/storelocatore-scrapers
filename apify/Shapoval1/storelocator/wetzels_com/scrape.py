import csv
import json
from lxml import html
from concurrent import futures
from sgrequests import SgRequests
from sgzip.static import static_coordinate_list, SearchableCountries


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


def get_data(coord):
    rows = []
    lat, lng = coord
    locator_domain = "https://www.wetzels.com"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
    }

    session = SgRequests()

    r = session.get(
        f"https://app.mapply.net/front-end/get_surrounding_stores.php?callback=jQuery3600903511324138744_1621886437294&api_key=mapply.5a691272962f97b2c2bbe503420c7d9a&latitude={lat}&longitude={lng}&max_distance=0&limit=100&calc_distance=0&callback=bold_sl.set_stores&_=1621886437300",
        headers=headers,
    )
    jsblock = r.text.split('"stores":')[1].split(',"you":false})')[0].strip()
    js = json.loads(jsblock)
    for j in js:

        page_url = "https://www.wetzels.com/find-a-location"
        desc = j.get("summary")
        detail = j.get("detailed")
        a = html.fromstring(desc)
        b = html.fromstring(detail)
        location_name = (
            "".join(a.xpath('//span[@class="name"]/text()')).strip() or "<MISSING>"
        )
        street_address = (
            " ".join(a.xpath('//span[@class="address"]/text()'))
            .replace("\n", "")
            .strip()
        )
        city = "".join(a.xpath('//span[@class="city"]/text()')).strip() or "<MISSING>"
        state = (
            "".join(a.xpath('//span[@class="prov_state"]/text()')).strip()
            or "<MISSING>"
        )
        postal = (
            "".join(a.xpath('//span[@class="postal_zip"]/text()')).strip()
            or "<MISSING>"
        )
        country_code = "US"
        if not postal.isdigit():
            country_code = "CA"
        store_number = j.get("store_id") or "<MISSING>"
        if location_name.find("Gila River Arena") != -1:
            store_number = "2633217"
        if location_name.find("Pacific Park Santa Monica Pier") != -1:
            store_number = "2633235"
        phone = (
            "".join(b.xpath('//span[@class="phone"]//text()')).strip() or "<MISSING>"
        )
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = "<MISSING>"

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
    s = set()
    coords = static_coordinate_list(radius=50, country_code=SearchableCountries.USA)

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, coord): coord for coord in coords}
        for future in futures.as_completed(future_to_url):
            rows = future.result()
            for row in rows:
                _id = row[8]
                if _id not in s:
                    s.add(_id)
                    out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
