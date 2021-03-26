import csv
import json

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


def get_js(params):
    city, country = params
    session = SgRequests()
    data = {
        "request": {
            "appkey": "FE424754-8D89-11E7-A07A-F839407E493E",
            "formdata": {
                "dataview": "store_default",
                "limit": 5000,
                "geolocs": {
                    "geoloc": [
                        {
                            "addressline": f"{city}",
                            "country": f"{country}",
                            "latitude": "",
                            "longitude": "",
                        }
                    ]
                },
                "searchradius": "5000",
                "where": {"country": {"eq": f"{country}"}},
            },
        }
    }

    r = session.post(
        "https://hosted.where2getit.com/fjallraven/rest/locatorsearch",
        data=json.dumps(data),
    )
    js = r.json()["response"]["collection"]
    return js


def fetch_data():
    out = []
    s = set()
    locator_domain = "https://www.fjallraven.com"
    page_url = "<MISSING>"
    countries = [("London", "UK"), ("Dallas", "US"), ("Ontario", "CA")]
    for params in countries:
        js = get_js(params)

        for j in js:
            store_number = j.get("clientkey") or "<MISSING>"
            if not store_number.isdigit():
                store_number = "<MISSING>"
            location_name = f"{j.get('name')}"
            street_address = j.get("address1") or "<MISSING>"
            street_address = " ".join(
                street_address.replace("_x005F_x000D_", " ").split()
            )
            city = j.get("city") or "<MISSING>"
            postal = j.get("postalcode") or "<MISSING>"
            if postal == "00000":
                postal = "<MISSING>"
            country_code = j.get("country") or "<MISSING>"
            if country_code == "CA" or country_code == "UK":
                state = j.get("province") or "<MISSING>"
            else:
                state = j.get("state") or "<MISSING>"

            if country_code == "UK":
                country_code = "GB"
                state = "<MISSING>"
            if country_code == "US" and state == "<MISSING>":
                continue

            phone = j.get("phone") or "<MISSING>"
            latitude = j.get("latitude") or "<MISSING>"
            longitude = j.get("longitude") or "<MISSING>"
            location_type = "<MISSING>"

            days = [
                "monday",
                "tuesday",
                "wednesday",
                "thursday",
                "friday",
                "saturday",
                "sunday",
            ]
            _tmp = []
            for day in days:
                part = day[:3]
                start = j.get(f"open_{part}")
                if start:
                    close = j.get(f"close_{part}")
                    _tmp.append(f"{day.capitalize()}: {start} - {close}")
                else:
                    _tmp.append(f"{day.capitalize()}: Closed")

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

            check = tuple(row[2:6])
            if check not in s:
                out.append(row)
                s.add(check)
    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
