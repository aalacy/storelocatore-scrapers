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
    locator_domain = "https://www.gominis.com"
    session = SgRequests()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
    }
    r = session.post(
        "https://www.gominis.com/locations/?CallAjax=GetLocations", headers=headers
    )
    js = r.json()
    for j in js:

        page_url = "https://www.gominis.com" + "".join(j.get("Path"))

        location_name = j.get("FriendlyName")
        phone = j.get("Phone")
        street_address = f"{j.get('Address1')} {j.get('Address2') or ''}".replace(
            "None", ""
        ).strip()
        city = j.get("City")
        state = j.get("State")
        postal = j.get("ZipCode")
        location_type = "<MISSING>"
        country_code = j.get("Country")
        store_number = "<MISSING>"
        latitude = j.get("Latitude")
        longitude = j.get("Longitude")
        hours_of_operation = "<MISSING>"
        cms = j.get("ComingSoon")
        if cms == 1:
            hours_of_operation = "Coming Soon"

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
