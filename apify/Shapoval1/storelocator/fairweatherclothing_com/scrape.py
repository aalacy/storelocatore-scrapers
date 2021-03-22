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
    locator_domain = "https://www.fairweatherclothing.com"
    api_url = "https://cdn.shopify.com/s/files/1/0047/1118/6550/t/16/assets/sca.storelocatordata.json?v=1601911640&origLat=45.492760499999996&origLng=-73.5614161&origAddress=311%20Rue%20Eleanor%2C%20Montr%C3%A9al%2C%20QC%20H3C%202C1%2C%20%D0%9A%D0%B0%D0%BD%D0%B0%D0%B4%D0%B0&formattedAddress=&boundsNorthEast=&boundsSouthWest="
    session = SgRequests()

    r = session.get(api_url)
    js = r.json()
    for j in js:

        page_url = "https://www.fairweatherclothing.com/pages/store-locator"
        location_name = j.get("name")
        street_address = j.get("address")
        phone = j.get("phone")
        city = j.get("city")
        state = j.get("state")
        country_code = j.get("country")
        store_number = "<MISSING>"
        latitude = j.get("lat")
        longitude = j.get("lng")
        location_type = "<MISSING>"
        hours_of_operation = "<MISSING>"
        postal = j.get("postal")
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
