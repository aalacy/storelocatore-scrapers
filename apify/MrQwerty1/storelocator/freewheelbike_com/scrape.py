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
    locator_domain = "https://www.freewheelbike.com/"
    api_url = "https://www.freewheelbike.com/webservices/ajax/storelocator.cfc?method=getGeojson"

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()["features"]

    for j in js:
        coords = j["geometry"]["coordinates"]
        longitude, latitude = coords
        j = j.get("properties")
        street_address = (
            f"{j.get('address_1')} {j.get('address_2') or ''}".strip() or "<MISSING>"
        )
        city = j.get("city") or "<MISSING>"
        state = j.get("state") or "<MISSING>"
        postal = j.get("zip") or "<MISSING>"
        country_code = "US"
        store_number = j.get("id") or "<MISSING>"
        page_url = f'https://www.freewheelbike.com{j.get("sefurl")}'
        location_name = j.get("descriptor")
        phone = j.get("phone") or "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = j.get("hours") or "<MISSING>"
        hours_of_operation = hours_of_operation.replace("<br />", ";")

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
