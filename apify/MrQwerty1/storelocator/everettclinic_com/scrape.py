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
    lat, lon = coord
    locator_domain = "https://www.everettclinic.com/"
    api_url = f"https://www.everettclinic.com/bin/optumcare/findlocations?businessName=&fullName=&latitude={lat}&longitude={lon}&isAcceptingNewPatients=true&radius=100mi&network=Everett"

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()["result"]["data"]["providers"]
    js = js.get("hits") or []

    for j in js:
        j = j["provider"]
        a = j.get("locations")[0].get("addressInfo")
        store_number = j.get("individualProviderId")
        page_url = f"https://www.everettclinic.com/provider-lookup/location.html?groupReferenceId={store_number}"
        location_name = j["providerInfo"]["businessName"]

        street_address = a.get("line1") or "<MISSING>"
        city = a.get("city") or "<MISSING>"
        state = a.get("state") or "<MISSING>"
        postal = a.get("zip") or "<MISSING>"
        country_code = "US"
        phone = j.get("locations")[0].get("telephoneNumbers")[0].get("telephoneNumber")

        latitude, longitude = a.get("lat_lon").split(",")

        _types = []
        types = (
            j.get("locations")[0]
            .get("plans")[0]
            .get("specialties")[0]
            .get("enrollment")
            or []
        )
        for t in types:
            _t = t.get("enrollmentRole") or ""
            _types.append(_t)

        location_type = ";".join(_types) or "<MISSING>"

        _tmp = []
        hours = j.get("locations")[0].get("hoursOfOperation") or []
        for h in hours:
            day = h.get("dayOfWeek").replace("One", "")
            start = h.get("fromHour")
            close = h.get("toHour")
            _tmp.append(f"{day}: {start} - {close}")

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
