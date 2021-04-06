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


def get_js(coords):
    session = SgRequests()
    lat, lng = coords

    data = {
        "request": {
            "appkey": "05D7DC22-D987-11E9-A0C5-022A407E493E",
            "formdata": {
                "dataview": "store_default",
                "limit": 5000,
                "geolocs": {
                    "geoloc": [
                        {
                            "addressline": "",
                            "country": "",
                            "latitude": f"{lat}",
                            "longitude": f"{lng}",
                        }
                    ]
                },
                "searchradius": "5000",
                "where": {"country": {"eq": ""}},
            },
        }
    }

    r = session.post(
        "https://hosted.where2getit.com/tommy/rest/locatorsearch", data=json.dumps(data)
    )
    js = r.json()["response"]["collection"]
    return js


def fetch_data():
    out = []
    locator_domain = "https://tommy.com/"

    coords = [("13.4665", "144.7928"), ("29.94654", "-90.062343")]
    for c in coords:
        js = get_js(c)

        for j in js:
            location_name = j.get("name")
            street_address = (
                f"{j.get('address1')} {j.get('address2') or ''}".strip() or "<MISSING>"
            )
            city = j.get("city") or "<MISSING>"
            postal = j.get("postalcode") or "<MISSING>"
            country_code = j.get("country") or "<MISSING>"
            if country_code == "CA":
                state = j.get("province") or "<MISSING>"
            else:
                state = j.get("state") or "<MISSING>"
            store_number = j.get("clientkey")

            phone = j.get("phone") or "<MISSING>"
            latitude = j.get("latitude") or "<MISSING>"
            longitude = j.get("longitude") or "<MISSING>"
            page_url = f"https://stores.tommy.com/{state.lower()}/{city.lower()}/{store_number}/"
            location_type = "<MISSING>"

            _tmp = []
            days = [
                "monday",
                "tuesday",
                "wednesday",
                "thursday",
                "friday",
                "saturday",
                "sunday",
            ]

            for day in days:
                start = j.get(f"{day}open")
                close = j.get(f"{day}close")

                if start and start != close:
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
            out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
