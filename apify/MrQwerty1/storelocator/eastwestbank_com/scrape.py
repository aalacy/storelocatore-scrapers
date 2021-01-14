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
    locator_domain = "https://www.eastwestbank.com/"
    api_url = "https://www.eastwestbank.com/en/BranchLocator/GetLocations?cache=false&latitude=40.713&longitude=-74.007&distance=5000&startIndex=0&endIndex=5000"

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()["Branches"]

    for j in js:
        street_address = (
            f"{j.get('Address1')} {j.get('Address2') or ''}".strip() or "<MISSING>"
        )
        city = j.get("City") or "<MISSING>"
        state = j.get("State") or "<MISSING>"
        postal = j.get("ZipCode") or "<MISSING>"
        country_code = "US"
        store_number = j.get("BranchNo") or "<MISSING>"
        page_url = f"https://www.eastwestbank.com/en/branch-locator/branch-details?id={j.get('Id')}"
        location_name = j.get("Name")
        phone = j.get("PhoneNumber") or "<MISSING>"
        latitude = j.get("Latitude") or "<MISSING>"
        longitude = j.get("Longitude") or "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = (
            j.get("LocationHours", "").replace("<br />", ";") or "<MISSING>"
        )

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
