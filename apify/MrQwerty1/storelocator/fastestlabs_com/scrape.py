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
    locator_domain = "https://www.fastestlabs.com/"
    api_url = "https://www.fastestlabs.com/locations/?CallAjax=GetLocations"

    session = SgRequests()
    r = session.post(api_url)
    js = r.json()

    for j in js:
        street_address = (
            f"{j.get('Address1')} {j.get('Address2') or ''}".strip() or "<MISSING>"
        )
        city = j.get("City") or "<MISSING>"
        state = j.get("State") or "<MISSING>"
        postal = j.get("ZipCode") or "<MISSING>"
        country_code = j.get("Country")
        if country_code == "USA":
            country_code = "US"
        store_number = j.get("ExternalID") or "<MISSING>"
        page_url = f'https://www.fastestlabs.com{j.get("Path")}'
        location_name = j.get("BusinessName")
        phone = j.get("Phone") or "<MISSING>"
        latitude = j.get("Latitude") or "<MISSING>"
        longitude = j.get("Longitude") or "<MISSING>"
        location_type = "<MISSING>"

        _tmp = []
        text = j.get("LocationHours")
        text = "[" + text.replace("[", "{").replace("]", "},")[:-1] + "]"
        hours = json.loads(text)
        for h in hours:
            day = h.get("Interval")
            start = h.get("OpenTime")
            close = h.get("CloseTime")

            isclosed = h.get("Closed")
            if isclosed == "1":
                _tmp.append(f"{day}: Closed")
            else:
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
        out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
