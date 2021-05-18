import csv
from concurrent import futures
from sgrequests import SgRequests
from sgzip.static import static_zipcode_list, SearchableCountries


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


def get_data(zip):
    rows = []

    locator_domain = "https://www.pitapitusa.com"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
    }
    session = SgRequests()
    r = session.get(
        f"https://liveapi.yext.com/v2/accounts/me/entities/geosearch?radius=50&location={zip}&limit=50&api_key=0044bc2f8e2fa0fe5019f2301f8cdd49&v=20181201&resolvePlaceholders=true&entityTypes=location",
        headers=headers,
    )
    js = r.json()
    for j in js["response"]["entities"]:
        a = j.get("address")
        page_url = j.get("c_baseURL") or f"https://locations.pitapitusa.com/?q={zip}"
        if page_url.find("https://pitapit.ca/") != -1:
            continue
        location_name = j.get("name") or "<MISSING>"
        street_address = f"{a.get('line1')} {a.get('line2') or ''}".strip()
        city = a.get("city") or "<MISSING>"
        state = a.get("region") or "<MISSING>"
        postal = a.get("postalCode") or "<MISSING>"
        country_code = a.get("countryCode") or "<MISSING>"
        store_number = "<MISSING>"
        phone = j.get("mainPhone") or "<MISSING>"
        latitude = j.get("yextDisplayCoordinate").get("latitude")
        longitude = j.get("yextDisplayCoordinate").get("longitude")
        location_type = "location"
        hours = j.get("hours")
        days = [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ]
        tmp = []
        for d in days:
            day = d
            try:
                closed = hours.get(d).get("isClosed")
            except:
                closed = True
            if not closed:
                start = hours.get(d).get("openIntervals")[0].get("start")
                close = hours.get(d).get("openIntervals")[0].get("end")
                line = f"{day} {start} - {close}"
                tmp.append(line)
            if closed:
                line = f"{day} - Closed"
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
    coords = static_zipcode_list(radius=50, country_code=SearchableCountries.USA)

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
