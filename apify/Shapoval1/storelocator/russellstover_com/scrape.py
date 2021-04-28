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

    locator_domain = "https://www.russellstover.com"
    api_url = "https://www.russellstover.com/wcsstore/storelocator-data/rsc_locations.json?origLat=35.988039&origLng=-83.545158&origAddress=1791%2520Sockless%2520Rd%252C%2520Dandridge%252C%2520TN%252037725%252C%2520%25D0%25A1%25D0%25A8%25D0%2590&formattedAddress=&boundsNorthEast=&boundsSouthWest=&storeId=11005&langId=-1&origLat=35.988039&origLng=-83.545158&origAddress=1791%2520Sockless%2520Rd%252C%2520Dandridge%252C%2520TN%252037725%252C%2520%25D0%25A1%25D0%25A8%25D0%2590&formattedAddress=&boundsNorthEast=&boundsSouthWest="
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()
    for j in js:
        page_url = j.get("web")
        location_name = j.get("name")
        street_address = f"{j.get('address')} {j.get('address2') or ''}".strip()
        phone = j.get("phone")
        state = j.get("state")
        postal = j.get("postal")
        country_code = "US"
        city = j.get("city")
        store_number = j.get("id")
        latitude = j.get("lat")
        longitude = j.get("lng")
        location_type = "<MISSING>"
        hours_of_operation = f"{j.get('hours1') or ''} {j.get('hours2') or ''} {j.get('hours3') or ''}".strip()

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
