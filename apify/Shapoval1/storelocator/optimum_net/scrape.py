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

    locator_domain = "https://www.optimum.net/"

    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }

    r = session.get(
        "https://www.optimum.net/api/map/services/v1//map/store/marker/search?area.maxLat=41.574418900097534&area.maxLon=-71.4052424587429&area.minLat=40.01505331678458&area.minLon=-75.6645501412571&byType=Optimum%20Store&pageSize=8&sortBy=distance",
        headers=headers,
    )
    js = r.json()["_embedded"]["results"]

    for j in js:

        store_number = (
            "".join(j.get("_links").get("self").get("href")).split("/")[-1].strip()
        )
        location_name = j.get("name")
        location_type = j.get("type")
        street_address = j.get("street")
        phone = j.get("phone")
        state = j.get("state")
        postal = j.get("zip")
        country_code = "US"
        city = j.get("city")
        page_url = "https://www.optimum.net/support/contact-us#/optimum-store"
        latitude = j.get("latLon").get("lat")
        longitude = j.get("latLon").get("lon")
        hours_of_operation = "".join(j.get("hours"))
        if hours_of_operation.find("(") != -1:
            hours_of_operation = hours_of_operation.split("(")[0].strip()

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
