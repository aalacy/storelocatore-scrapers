import csv
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
    locator_domain = "https://www.citybbq.com/"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Referer": "https://www.citybbq.com/",
        "ui-cache-ttl": "300",
        "ui-transformer": "restaurants",
        "clientid": "citybbq",
        "Content-Type": "application/json",
        "nomnom-platform": "web",
        "Origin": "https://www.citybbq.com",
        "Connection": "keep-alive",
        "TE": "Trailers",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }

    session = SgRequests()

    r = session.get(
        f"https://nomnom-prod-api.citybbq.com/restaurants/near?lat={lat}&long={lng}&radius=20000&limit=6&nomnom=calendars&nomnom_calendars_from=20210715&nomnom_calendars_to=20210723&nomnom_exclude_extref=999",
        headers=headers,
    )
    js = r.json()["restaurants"]

    for j in js:

        page_url = j.get("url")

        location_name = j.get("storename")
        street_address = j.get("streetaddress")
        city = j.get("city")
        state = j.get("state")
        postal = j.get("zip")
        country_code = j.get("country")
        store_number = "<MISSING>"
        phone = j.get("telephone")
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        location_type = "<MISSING>"
        try:
            hours = j.get("calendars").get("calendar")[0].get("ranges") or "<MISSING>"
        except:
            hours = "<MISSING>"
        tmp = []
        if hours != "<MISSING>":
            for h in hours:
                day = h.get("weekday")
                start = "".join(h.get("start")).split()[1].strip()
                end = "".join(h.get("end")).split()[1].strip()
                line = f"{day} {start} - {end}"
                tmp.append(line)
            hours_of_operation = ";".join(tmp) or "<MISISNG>"
        else:
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
                _id = row[3]
                if _id not in s:
                    s.add(_id)
                    out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
