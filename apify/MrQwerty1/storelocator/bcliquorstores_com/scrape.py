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
    locator_domain = "https://www.bcliquorstores.com/"
    api_url = "https://www.bcliquorstores.com/stores/search?format=json"

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()["stores"]

    for j in js:
        street_address = (
            f"{j.get('addressLine1')} {j.get('addressLine2') or ''}".strip()
            or "<MISSING>"
        )

        city = j.get("city") or "<MISSING>"
        state = j.get("province") or "<MISSING>"
        postal = j.get("postalCode") or "<MISSING>"
        country_code = "CA"
        store_number = j.get("storeNumber") or "<MISSING>"
        location_name = j.get("name") or "<MISSING>"
        phone = j.get("phone") or "<MISSING>"
        latitude = j.get("latitude") or "<MISSING>"
        longitude = j.get("longitude") or "<MISSING>"
        location_type = "<MISSING>"
        page_url = f"https://www.bcliquorstores.com/store/locator/{store_number}"

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
        hours = j.get("hours") or []

        for d, h in zip(days, hours):
            try:
                start = h.get("open")
                end = h.get("close")
                _tmp.append(f"{d}: {start} - {end}")
            except AttributeError:
                _tmp.append(f"{d}: Closed")

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
