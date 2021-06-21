import csv
import json

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


def fetch_data():
    out = []
    s = set()
    locator_domain = "https://www.everettclinic.com/"
    api_url = "https://www.everettclinic.com/bin/optumcare/findlocations"
    session = SgRequests()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "uk-UA,uk;q=0.8,en-US;q=0.5,en;q=0.3",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "CSRF-Token": "undefined",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://www.everettclinic.com",
        "Connection": "keep-alive",
        "Referer": "https://www.everettclinic.com/",
    }

    coords = static_coordinate_list(radius=100, country_code=SearchableCountries.USA)

    for coord in coords:
        lat, lng = coord
        data = {
            "search": "",
            "radius": "100mi",
            "isAcceptingNewPatients": True,
            "latitude": lat,
            "longitude": lng,
            "network": "Everett",
        }

        r = session.post(api_url, headers=headers, data=json.dumps(data))
        js = r.json()["result"]["data"]["providers"]
        js = js.get("hits") or []

        for j in js:
            j = j["provider"]
            a = j.get("locations")[0].get("addressInfo")
            store_number = j.get("individualProviderId")
            if store_number in s:
                continue

            s.add(store_number)
            page_url = f"https://www.everettclinic.com/locations-nav/locations/-/-/{store_number}.html"
            try:
                location_name = j["providerInfo"]["businessName"]
            except KeyError:
                continue

            street_address = a.get("line1") or "<MISSING>"
            city = a.get("city") or "<MISSING>"
            state = a.get("state") or "<MISSING>"
            postal = a.get("zip") or "<MISSING>"
            country_code = "US"
            phone = (
                j.get("locations")[0].get("telephoneNumbers")[0].get("telephoneNumber")
            )

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
            if hours_of_operation != "<MISSING>":
                days = [
                    "Monday",
                    "Tuesday",
                    "Wednesday",
                    "Thursday",
                    "Friday",
                    "Saturday",
                    "Sunday",
                ]
                for d in days:
                    if d not in hours_of_operation:
                        hours_of_operation += f";{d}: Closed"

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

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
