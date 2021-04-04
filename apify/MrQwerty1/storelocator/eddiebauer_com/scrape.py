import base64
import csv

from sgzip.static import static_coordinate_list, SearchableCountries
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


def fetch_data():
    out = []
    s = set()
    coords = static_coordinate_list(radius=200, country_code=SearchableCountries.USA)
    session = SgRequests()
    page_url = "<MISSING>"
    location_type = "<MISSING>"
    locator_domain = "https://www.eddiebauer.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
        "Accept": "*/*",
        "Origin": "https://www.eddiebauer.com",
        "Sec-Fetch-Site": "cross-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
    }

    for c in coords:
        lat, lon = c

        dog = f"Authorization=R8-Gateway%20App%3Dr8connect%2C%20key%3D4k2wIG8pFMUXvQnpRNmnAq%2C%20Type%3DSameOrigin&X-Domain-Id=eddiebauer&Geo-Position={lat}%3B{lon}&X-Device-Id=c650e12d-1fe7-0de9-4238-b44f60b8cb78&X-Request-Tag=zlZyUt2%2Bn0GaBoE07w7mtI4Dpaymj570o9dLxXZNY9kLc8qDuY4xigPU3CnEfA0aWNKF7BIxdIo%2BjWMKM7aEbw%3D%3D%23MTcxODM5&"
        hdog = base64.b64encode(dog.encode("utf8")).decode("utf8")
        params = (("lat", lat), ("radius", "200"), ("lng", lon), ("hdog", hdog))

        r = session.get(
            "https://platform.radius8.com/api/v1/streams/stores",
            headers=headers,
            params=params,
        )
        js = r.json()["results"]

        for j in js:
            _id = j.get("store_code")
            if _id in s:
                continue

            location_name = j.get("name") or "<MISSING>"
            if location_name.find("not real") != -1:
                continue

            a = j.get("address", {}) or {}
            street_address = (
                f'{a.get("address1")} {a.get("address2") or ""}'.strip() or "<MISSING>"
            )
            city = a.get("city") or "<MISSING>"
            state = a.get("state") or "<MISSING>"
            postal = a.get("postal_code") or "<MISSING>"
            if len(postal) == 4:
                postal = f"0{postal}"

            country = a.get("country") or "<MISSING>"
            if country == "USA":
                country_code = "US"
            else:
                country_code = "CA"

            store_number = _id
            phone = j.get("contact_info", {}).get("phone") or "<MISSING>"
            g = j.get("geo_point", {}) or {}
            latitude = g.get("lat") or "<MISSING>"
            longitude = g.get("lng") or "<MISSING>"

            _tmp = []
            days = [
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
                "Sunday",
            ]
            h = j.get("hours", {}) or {}

            for d in days:
                key = d[:3].lower()
                start = h[key][0]
                close = h[key][1]

                if start.lower().find("closed") != -1:
                    _tmp.append(f"{d}: Closed")
                else:
                    _tmp.append(
                        f"{d}: {start[:2]}:{start[2:]} - {close[:2]}:{close[2:]}"
                    )

            hours_of_operation = ";".join(_tmp) or "<MISSING>"
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

            out.append(row)
            s.add(_id)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
