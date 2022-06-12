import csv
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
    locator_domain = "https://www.lifemark.ca/"
    api_url = "https://www.lifemark.ca/locations/searchcallback"

    data = {
        "address": "",
        "lat": "51.5621883",
        "lng": "-88.2596971",
        "max_kilometers": "1000000",
        "result_limit": "350",
        "services": "[]",
        "provinces": "[]",
        "current_path": "locations",
    }

    session = SgRequests()
    r = session.post(api_url, data=data)
    js = r.json()["results"]

    for j in js:
        street_address = (
            f"{j.get('Address1')} {j.get('Additional') or ''}".strip() or "<MISSING>"
        )
        city = j.get("City") or "<MISSING>"
        state = j.get("Province") or "<MISSING>"
        postal = j.get("PostalCode") or "<MISSING>"
        country_code = "CA"
        store_number = j.get("ClinicId") or "<MISSING>"
        page_url = f'https://www.lifemark.ca/{j.get("url_alias")}'
        location_name = j.get("ClinicName") or city
        phone = j.get("Phone") or "<MISSING>"
        latitude = j.get("Latitude") or "<MISSING>"
        longitude = j.get("Longitude") or "<MISSING>"
        location_type = "<MISSING>"

        _tmp = []
        hours = j.get("hours") or {}
        for k, v in hours.items():
            _tmp.append(f"{k.capitalize()}: {v}")

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
