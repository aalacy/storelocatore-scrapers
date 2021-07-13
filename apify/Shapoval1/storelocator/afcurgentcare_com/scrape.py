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
    locator_domain = "https://www.wetzels.com"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
    }

    session = SgRequests()

    r = session.get(
        f"https://afcurgentcare.com/modules/multilocation/?near_lat={lat}&near_lon={lng}&services__in=&published=1&within_business=true",
        headers=headers,
    )

    js = r.json()
    for j in js["objects"]:

        page_url = j.get("location_url")
        location_name = j.get("location_name")
        street_address = (
            f"{j.get('street')} {j.get('street2') or ''}".replace("None", "").strip()
            or "<MISSING>"
        )
        city = j.get("city")
        state = j.get("state")
        postal = j.get("postal_code")
        country_code = j.get("country")
        store_number = "<MISSING>"
        phone = j.get("phonemap").get("phone")
        latitude = j.get("lon")
        longitude = j.get("lat")
        location_type = "<MISSING>"
        hours = j.get("formatted_hours").get("primary").get("days")
        tmp = []
        for h in hours:
            day = h.get("label")
            time = h.get("content")
            line = f"{day} {time}"
            tmp.append(line)
        hours_of_operation = ";".join(tmp) or "<MISSING>"
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
    coords = static_coordinate_list(radius=35, country_code=SearchableCountries.USA)

    with futures.ThreadPoolExecutor(max_workers=8) as executor:
        future_to_url = {executor.submit(get_data, coord): coord for coord in coords}
        for future in futures.as_completed(future_to_url):
            rows = future.result()
            for row in rows:
                _id = row[1]
                if _id not in s:
                    s.add(_id)
                    out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
