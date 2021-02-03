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
    locator_domain = "https://www.deseretindustries.org/"
    api_url = "https://www.deseretindustries.org/api/store-locations"

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()["store"]

    for j in js:
        a = j.get("address").get("line")
        street_address = a[0]
        line = a[1]
        if line.find(",") == -1:
            line = a[-1]

        if line.find(",") != -1:
            city = line.split(",")[0].strip()
            line = line.split(",")[1].strip()
            state = line.split()[0]
            postal = line.split()[1]
        else:
            postal = line.split()[-1]
            state = line.split()[-2]
            city = " ".join(line.split()[:-2])
        country_code = "US"
        store_number = j.get("id")
        page_url = f"https://www.deseretindustries.org/locations/{store_number}"
        location_name = j.get("name")
        phone = j.get("phone") or "<MISSING>"
        latitude = j.get("latitude") or "<MISSING>"
        longitude = j.get("longitude") or "<MISSING>"
        location_type = "<MISSING>"

        _tmp = []
        hours = j.get("storeHours", {}).get("storeHour") or []
        for h in hours:
            day = h.get("day")
            time = h.get("time")
            _tmp.append(f"{day}: {time}")

        hours_of_operation = ";".join(_tmp) or "<MISSING>"
        if location_name.lower().find("closed") != -1:
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
