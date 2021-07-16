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
    countries = ["United States", "United Kingdom"]
    locator_domain = "https://www.bondno9.com/"
    api_url = "https://www.bondno9.com/front/app/store/countries"
    page_url = "https://www.bondno9.com/stores.html"

    session = SgRequests()
    r = session.get(api_url)
    for c in countries:
        js = r.json()[c]
        country_code = "US"
        if "King" in c:
            country_code = "GB"

        for j in js:
            j = j.get("store")
            a = j.get("address")
            street_address = (
                f"{a.get('address1')} {a.get('address2') or ''}".replace(
                    "None", ""
                ).strip()
                or "<MISSING>"
            )
            city = a.get("city") or "<MISSING>"
            state = a.get("province") or "<MISSING>"
            postal = a.get("postalCode") or "<MISSING>"
            store_number = j.get("storeId") or "<MISSING>"
            location_name = j.get("name")
            phone = j.get("phoneNumber") or "<MISSING>"
            latitude = j.get("latitude") or "<MISSING>"
            longitude = j.get("longitude") or "<MISSING>"
            location_type = j.get("storeType") or "<MISSING>"
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
