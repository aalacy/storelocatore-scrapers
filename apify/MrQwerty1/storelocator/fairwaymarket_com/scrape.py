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
    locator_domain = "https://www.fairwaymarket.com/"
    page_url = "https://www.fairwaymarket.com/sm/planning/rsid/183/store"

    headers = {"X-Site-Host": "https://www.fairwaymarket.com"}

    session = SgRequests()
    r = session.get(
        "https://storefrontgateway.brands.wakefern.com/api/stores", headers=headers
    )
    js = r.json()["items"]

    for j in js:
        street_address = (
            f"{j.get('addressLine1')} {j.get('addressLine2') or ''}".strip()
            or "<MISSING>"
        )
        city = j.get("city") or "<MISSING>"
        state = j.get("countyProvinceState") or "<MISSING>"
        postal = j.get("postCode") or "<MISSING>"
        country_code = "US"
        store_number = j.get("retailerStoreId") or "<MISSING>"
        location_name = j.get("name")
        phone = j.get("phone") or "<MISSING>"
        loc = j.get("location")
        latitude = loc.get("latitude") or "<MISSING>"
        longitude = loc.get("longitude") or "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = j.get("openingHours") or "<MISSING>"
        hours_of_operation = hours_of_operation.replace("\n", "")

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
