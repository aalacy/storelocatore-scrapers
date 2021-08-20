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
    locator_domain = "https://www.bankofcolorado.com"
    api_url = "https://www.bankofcolorado.com/locator/json?lat=40.806862&lon=-96.681679&dist=100&limit=150&showLocations=0&showAtms=0"
    session = SgRequests()

    r = session.get(api_url)

    js = r.json()
    for j in js["branches"]:
        location_name = "<MISSING>"
        street_address = j.get("address1")
        city = j.get("city")
        state = "".join(j.get("address3")).split(",")[1].split()[0]
        page_url = "https://www.bankofcolorado.com/location-search"
        country_code = "US"
        postal = "".join(j.get("address3")).split(",")[1].split()[1]
        if postal.find("-") != -1:
            postal = postal.split("-")[0].strip()
        store_number = "<MISSING>"
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        try:
            location_type = j.get("services")[0]
        except IndexError:
            continue
        if "".join(location_type).find("Full-Service") == -1:
            continue
        hours_of_operation = (
            " ".join(j.get("lobbyHours"))
            .replace("(By Appointment Only)", "")
            .replace("Free Parking Available", "")
            .strip()
        )
        phone = j.get("phone")

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
