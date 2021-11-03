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


def fetch_data():
    out = []
    locator_domain = "https://mattressbyappointment.com/"
    api_url = "https://mattressbyappointment.com/api/v1/?api_key=a80043c84c84c890157f4fcbbf813e564bb1ce544453b7adf62992a9&event=dealer-locator"

    session = SgRequests()
    r = session.get(api_url)
    text = r.text.replace("mbaDealerLocator(", "").replace(");", "")
    js = json.loads(text)

    for j in js:
        street_address = j.get("address") or "<MISSING>"
        city = j.get("city") or "<MISSING>"
        state = j.get("state") or "<MISSING>"
        postal = j.get("postal") or "<MISSING>"
        country_code = "US"
        store_number = "<MISSING>"
        page_url = j.get("web")
        location_name = j.get("name")
        phone = j.get("phone") or "<MISSING>"
        if " " in phone:
            phone = phone.split()[-1]
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
        location_type = "<MISSING>"

        _tmp = []
        hours = j.get("availability")
        if type(hours) is dict:
            for k, v in hours.items():
                _tmp.append(f"{k}: {v}")

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
        out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
