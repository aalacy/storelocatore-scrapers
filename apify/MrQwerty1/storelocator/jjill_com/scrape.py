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


def get_js():
    session = SgRequests()
    data = {
        "request": {
            "appkey": "28CEC02A-6278-11E7-93CD-BD7155A65BB0",
            "formdata": {
                "dataview": "store_default",
                "limit": 5000,
                "geolocs": {
                    "geoloc": [
                        {
                            "addressline": "30313",
                            "country": "",
                            "latitude": "",
                            "longitude": "",
                        }
                    ]
                },
                "searchradius": "5000",
                "where": {"country": {"eq": "US"}},
            },
        }
    }

    r = session.post(
        "https://hosted.where2getit.com/jjill/rest/locatorsearch", data=json.dumps(data)
    )
    js = r.json()["response"]["collection"]
    return js


def fetch_data():
    out = []
    url = "https://www.jjill.com/"
    js = get_js()
    for j in js:
        locator_domain = url
        location_name = f"{j.get('name')}"
        street_address = (
            f"{j.get('address1')} {j.get('address2') or ''}".strip() or "<MISSING>"
        )
        city = j.get("city") or "<MISSING>"
        postal = j.get("postalcode") or "<MISSING>"
        country_code = j.get("country") or "<MISSING>"
        state = j.get("state") or "<MISSING>"
        store_number = j.get("clientkey")
        phone = j.get("phone") or "<MISSING>"
        latitude = j.get("latitude") or "<MISSING>"
        longitude = j.get("longitude") or "<MISSING>"
        page_url = f"https://locations.jjill.com/{state}/{city}/{store_number}/"
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
            if day == "tuesday":
                part = "tues"
            elif day == "thursday":
                part = "thurs"
            else:
                part = day[:3]
            start = j.get(f"{part}_open")
            if start and start != "CLOSED":
                close = j.get(f"{part}_close")
                _tmp.append(f"{day.capitalize()}: {start} - {close}")
            else:
                _tmp.append(f"{day.capitalize()}: Closed")

        if _tmp:
            hours_of_operation = ";".join(_tmp)

            if hours_of_operation.count("Closed") == 7:
                continue
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
        out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
