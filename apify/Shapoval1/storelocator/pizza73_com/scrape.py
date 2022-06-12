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
    locator_domain = "https://www.pizza73.com"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "X-Requested-With": "XMLHttpRequest",
        "Connection": "keep-alive",
        "Referer": "https://www.pizza73.com/Pizza73/pizza-73-locations",
    }

    session = SgRequests()

    try:
        r = session.get(
            f"https://www.pizza73.com/Pizza73/proxy.php?lng={lng}&lat={lat}",
            headers=headers,
        )
        js = r.json()
        for j in js["data"]:

            page_url = "https://www.pizza73.com/Pizza73/pizza-73-locations"
            location_name = "Pizza 73"
            street_address = (
                f"{j.get('streetNumber') or ''} {j.get('ADDRESS_LINE_1') or ''}".strip()
            )
            city = j.get("CITY")
            state = j.get("PROVINCE")
            postal = j.get("POSTAL_CODE")
            country_code = "CA"
            store_number = j.get("STORE_ID")
            phone = j.get("STORE_PHONE_NO")
            latitude = j.get("storeLatitude")
            longitude = j.get("storeLongitude")
            location_type = "<MISSING>"
            hours_of_operation = "".join(j.get("OPERATING_HOUR_SET")).replace(
                "<br>", " "
            )

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
    except:
        pass

    return rows


def fetch_data():
    out = []
    s = set()
    coords = static_coordinate_list(radius=20, country_code=SearchableCountries.CANADA)

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
