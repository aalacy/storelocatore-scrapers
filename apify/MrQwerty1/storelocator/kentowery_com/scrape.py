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
    locator_domain = "https://www.kentowery.com/"
    api_url = "https://www.kentowery.com/wp-json/monro/v1/stores/brand?brand=4"

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()["data"]

    for j in js:
        street_address = (
            f"{j.get('Address')} {j.get('Address2') or ''}".strip() or "<MISSING>"
        )
        city = j.get("City") or "<MISSING>"
        state = j.get("StateCode") or "<MISSING>"
        postal = j.get("ZipCode") or "<MISSING>"
        country_code = "US"
        store_number = j.get("Id") or "<MISSING>"
        page_url = "https://www.kentowery.com/store-search/?redirect=%2F"
        location_name = j.get("BrandDisplayNameShort") or "<MISSING>"
        phone = j.get("SalesPhone") or "<MISSING>"
        latitude = j.get("Latitude") or "<MISSING>"
        longitude = j.get("Longitude") or "<MISSING>"
        location_type = "<MISSING>"

        _tmp = []
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
            start = j.get(f"{d}OpenTime")
            close = j.get(f"{d}CloseTime")
            if start != close:
                _tmp.append(f"{d}: {start} - {close}")
            else:
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
