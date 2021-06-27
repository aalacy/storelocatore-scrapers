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

    locator_domain = "https://www.fcbanking.com"
    api_url = "https://www.fcbanking.com/umbraco/surface/LocationSurface/GetAllBranchLocationsJSON?_=1624124908409"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()

    for j in js:
        slug = j.get("url")
        page_url = f"{locator_domain}{slug}"
        location_name = j.get("Name")
        location_type = "Branch"
        street_address = j.get("StreetAddress")
        state = j.get("StateCode")
        postal = j.get("PostalCode")
        country_code = "USA"
        city = j.get("City")
        store_number = j.get("ID")
        latitude = j.get("Latitude")
        longitude = j.get("Longitude")
        phone = j.get("Phone")
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        tmp = []
        for d in days:
            times = j.get(f"BranchLobbyHours_{d}")
            if times is None:
                continue
            line = f"{d} {times}"
            tmp.append(line)
        hours_of_operation = ";".join(tmp) or "<MISSING>"

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
