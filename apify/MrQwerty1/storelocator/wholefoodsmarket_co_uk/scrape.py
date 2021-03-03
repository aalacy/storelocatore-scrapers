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
    locator_domain = "https://www.wholefoodsmarket.co.uk/"
    api_url = "https://www.wholefoodsmarket.co.uk/staticData/Z26G8nI.json"

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()["siteData"]["stores"]

    for j in js:
        street_address = (
            f"{j.get('address')} {j.get('address2') or ''}".strip() or "<MISSING>"
        )
        city = j.get("city") or "<MISSING>"
        state = j.get("metro_area") or "<MISSING>"
        postal = j.get("zip_code") or "<MISSING>"
        country_code = "GB"
        store_number = j.get("") or "<MISSING>"
        page_url = f'https://www.wholefoodsmarket.co.uk/stores/{j.get("folder")}'
        location_name = j.get("name")
        phone = j.get("phone") or "<MISSING>"
        loc = j.get("geo_location").get("coordinates")
        latitude = loc[1] or "<MISSING>"
        longitude = loc[0] or "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = j.get("hours") or "<MISSING>"
        if hours_of_operation.find("*") != -1:
            hours_of_operation = hours_of_operation.split("*")[0].strip()

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
