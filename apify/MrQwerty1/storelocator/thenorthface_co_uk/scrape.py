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
            "appkey": "3A992F50-193E-11E5-91BC-C90E919C4603",
            "formdata": {
                "dataview": "store_default",
                "limit": 500,
                "geolocs": {
                    "geoloc": [
                        {
                            "addressline": "",
                            "country": "UK",
                            "latitude": "",
                            "longitude": "",
                        }
                    ]
                },
                "searchradius": "5000",
                "where": {"country": {"eq": ""}},
            },
        }
    }

    r = session.post(
        "https://hosted.where2getit.com/northfaceeuuk/rest/locatorsearch",
        data=json.dumps(data),
    )
    js = r.json()["response"]["collection"]
    return js


def fetch_data():
    out = []
    s = set()
    url = "https://www.thenorthface.co.uk/"
    page_url = "https://www.thenorthface.co.uk/store-locator.html"
    js = get_js()

    for j in js:
        locator_domain = url
        location_name = f"{j.get('name')}"
        if location_name.lower().find("north face") == -1:
            continue
        street_address = j.get("address1") or "<MISSING>"
        city = j.get("city") or "<MISSING>"
        postal = j.get("postalcode") or "<MISSING>"
        country_code = j.get("country") or "<MISSING>"
        if country_code != "UK":
            continue
        state = j.get("province") or "<MISSING>"
        store_number = j.get("clientkey")
        if store_number in s:
            continue

        s.add(store_number)
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
            if day == "thursday":
                part = "thu"
            elif day == "saturday" or day == "sunday":
                part = "".join(day[:2])
            else:
                part = day[0]
            time = j.get(part) or "Closed"
            if time.lower().find("orders") != -1:
                time = "Closed"
            _tmp.append(f"{day.capitalize()}: {time}")

        hours_of_operation = ";".join(_tmp) or "<MISSING>"

        if hours_of_operation.lower().count("closed") == 7:
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
