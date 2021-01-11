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
    locator_domain = "https://smokeybones.com/"
    api_url = "https://api.togoorder.com/api/GetLocationMap/3214?lastMaxId=0&pageSize=500&isUnlisted=false"

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()

    for j in js:
        street_address = (
            f"{j.get('Address1')} {j.get('Address2') or ''}".strip() or "<MISSING>"
        )
        city = j.get("City") or "<MISSING>"
        state = j.get("State") or "<MISSING>"
        postal = j.get("Zip") or "<MISSING>"
        country_code = "US"
        store_number = j.get("Id") or "<MISSING>"
        page_url = "https://order.smokeybones.com/#!/"
        location_name = j.get("LocationName")
        phone = j.get("Phone") or "<MISSING>"
        latitude = j.get("Lat") or "<MISSING>"
        longitude = j.get("Long") or "<MISSING>"
        location_type = "<MISSING>"

        _tmp = []
        hours = j.get("OrderTypeViewModels")
        for h in hours:
            if h.get("OrderType") != 2:
                continue

            days = h["HoursOfOperation"]["WeekdayHours"]
            for d in days:
                day = d.get("WeekDay")
                start = d.get("StartTime")
                close = d.get("StopTime").replace("1.", "")
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
