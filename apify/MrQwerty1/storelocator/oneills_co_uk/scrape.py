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


def get_page_url(_id):
    session = SgRequests()
    r = session.get(f"https://www.oneills.co.uk/cborms/pub/brands/521/outlets/{_id}")
    js = r.json()
    slug = js.get("outletStructure").get("uri")
    if slug:
        return f"https://www.oneills.co.uk{slug}"
    return "<MISSING>"


def fetch_data():
    out = []
    locator_domain = "https://www.oneills.co.uk/"
    api_url = "https://www.oneills.co.uk/cborms/pub/brands/521/outlets/"

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()

    for j in js:
        a = j.get("address")
        street_address = a.get("line1") or "<MISSING>"
        city = a.get("town") or "<MISSING>"
        state = a.get("county") or "<MISSING>"
        postal = a.get("postcode") or "<MISSING>"
        country_code = "GB"
        store_number = j.get("bunCode") or "<MISSING>"
        page_url = get_page_url(store_number)
        location_name = j.get("name")
        phone = j.get("telephoneNumber") or "<MISSING>"
        g = j.get("gpsCoordinates")
        latitude = g.get("latitude") or "<MISSING>"
        longitude = g.get("longitude") or "<MISSING>"
        location_type = "<MISSING>"

        status = j.get("status")
        if status == "TEMP_CLOSED":
            hours_of_operation = "Temporarily Closed"
        else:
            hours_of_operation = "<MISSING>"

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
