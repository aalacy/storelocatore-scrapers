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
    locator_domain = "https://semichem.co.uk/"
    page_url = "https://semichem.co.uk/store-finder/"
    api_url = "https://semichem.co.uk/store-finder/stores/"

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()

    for j in js:
        street_address = j.get("address_line_1") or "<MISSING>"
        city = j.get("address_line_2") or "<MISSING>"
        state = j.get("address_line_3") or "<MISSING>"
        postal = j.get("postcode") or "<MISSING>"
        country_code = "GB"
        store_number = j.get("store_id") or "<MISSING>"
        location_name = j.get("title") or "<MISSING>"
        phone = j.get("telephone_number") or "<MISSING>"
        latitude = j.get("latitude") or "<MISSING>"
        longitude = j.get("longitude") or "<MISSING>"
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
        for d in days:
            part = d[:3]
            start = j.get(f"ot_{part}_open")
            close = j.get(f"ot_{part}_close")
            if not close:
                _tmp.append(f"{d.capitalize()}: Closed")
            else:
                _tmp.append(
                    f"{d.capitalize()}: {start[:2]}:{start[2:]} - {close[:2]}:{close[2:]}"
                )

        hours_of_operation = ";".join(_tmp) or "<MISSING>"

        row = [
            locator_domain,
            page_url,
            location_name,
            street_address.strip(),
            city.strip(),
            state.strip(),
            postal.strip(),
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
