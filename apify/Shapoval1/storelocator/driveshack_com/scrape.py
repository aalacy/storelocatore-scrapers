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

    locator_domain = "https://www.driveshack.com"
    api_url = "https://www.driveshack.com/page-data/locations/page-data.json"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()["result"]["data"]["allContentfulDriveShackLocations"]["edges"]
    for j in js:
        a = j.get("node")
        slug = a.get("slug")

        session = SgRequests()
        r = session.get(
            f"https://www.driveshack.com/page-data/locations/{slug}/page-data.json",
            headers=headers,
        )
        js = r.json()["result"]["data"]["contentfulDriveShackLocations"]

        page_url = f"{locator_domain}/{slug}"
        location_type = "<MISSING>"
        street_address = js.get("address1")
        phone = "<MISSING>"
        state = js.get("state")
        postal = js.get("zipCode")
        country_code = "USA"
        city = js.get("city")
        store_number = "<MISSING>"
        latitude = js.get("locationCoordinates").get("lat")
        longitude = js.get("locationCoordinates").get("lon")
        location_name = js.get("locationName")
        hours = js.get("hoursOfOperation").get("tableData")
        tmp = []
        for h in hours[1:]:
            day = h[0]
            time = h[1]
            line = f"{day} {time}"
            tmp.append(line)

        hours_of_operation = "; ".join(tmp) or "<MISSING>"

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
