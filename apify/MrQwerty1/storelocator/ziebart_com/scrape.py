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
    locator_domain = "https://ziebart.com"
    api_url = "https://api.uniglassplus.com/api/stores?page=1&itemsPerPage=3000&isZiebart=true&locale=en"

    headers = {
        "accept": "application/json",
    }

    session = SgRequests()
    r = session.get(api_url, headers=headers)
    js = r.json()

    for j in js:
        street_address = j.get("streetAddress") or "<MISSING>"
        city = j.get("city") or "<MISSING>"
        state = j.get("state") or "<MISSING>"
        postal = j.get("zipCode") or "<MISSING>"
        country_code = "CA"
        store_number = j.get("storeId") or "<MISSING>"
        page_url = f'https://www.uniglassplus.com/locations/{j.get("slug")}'
        location_name = j.get("name")
        phone = j.get("phone") or "<MISSING>"
        latitude = j.get("latitude") or "<MISSING>"
        longitude = j.get("longitude") or "<MISSING>"
        if longitude == "0":
            longitude = "<MISSING>"
        location_type = "<MISSING>"

        _tmp = []
        hours = j.get("storesAvailabilities") or []
        for h in hours:
            t = h.get("weekDay")
            if t == "WORKDAY":
                day = "Mon-Fri"
            elif t == "WEEKEND":
                day = "Sat-Sun"
            else:
                day = t

            start = h.get("openTime")
            end = h.get("closedTime")
            if start and "By" not in start:
                _tmp.append(f"{day}:  {start} - {end}")
            elif start and "By" in start:
                _tmp.append(f"{day}: {start}")
            else:
                _tmp.append(f"{day}: Closed")

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
