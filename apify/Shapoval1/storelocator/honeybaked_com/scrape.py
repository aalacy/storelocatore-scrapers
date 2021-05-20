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
    locator_domain = "https://www.honeybaked.com/"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
    }

    session = SgRequests()

    r = session.get(
        f"https://www.honeybaked.com/api/store/v1/?long={lng}&lat={lat}&radius=100",
        headers=headers,
    )
    js = r.json()
    for j in js:

        a = j.get("storeInformation")

        location_name = a.get("name")
        street_address = (
            f"{a.get('address1')} {a.get('address2') or ''}".replace("None", "")
            .replace("<b>", "")
            .replace("</b>", "")
            .strip()
        )
        city = a.get("city")
        state = a.get("state")
        postal = a.get("zipCode")
        country_code = "US"
        store_number = a.get("storeId")
        page_url = f"https://www.honeybaked.com/stores/{store_number}"
        phone = a.get("phoneNumber") or "<MISSING>"
        latitude = a.get("location").get("coordinates")[1]
        longitude = a.get("location").get("coordinates")[0]
        location_type = a.get("storeType")
        hours = a.get("storeHours")
        hours_of_operation = "<MISSING>"
        if hours is not None:
            tmp = []
            for h in hours:
                days = (
                    str(h.get("dayOfTheWeek"))
                    .replace("0", "Sun")
                    .replace("1", "Mon")
                    .replace("2", "Tue")
                    .replace("3", "Wed")
                    .replace("4", "Thu")
                    .replace("5", "Fri")
                    .replace("6", "Sat")
                )
                open = h.get("openTime")
                close = h.get("closeTime")
                closed = h.get("closed")
                line = f"{days} {open} - {close}"
                if closed:
                    line = f"{days} - Closed"
                tmp.append(line)
            hours_of_operation = ";".join(tmp)
            if hours_of_operation.count("Closed") == 7:
                hours_of_operation = "Closed"

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
    coords = static_coordinate_list(radius=100, country_code=SearchableCountries.USA)

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
