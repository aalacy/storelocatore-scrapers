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
    url = "https://www.fidelity.com/"
    api_url = "https://www.fidelity.com/customer-service/branches/system/BLJSON"

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()

    for j in js:
        locator_domain = url
        location_name = j.get("branch") or "<MISSING>"
        street_address = (
            f"{j.get('address1')} {j.get('address2') or ''}".strip() or "<MISSING>"
        )
        city = j.get("city") or "<MISSING>"
        state = j.get("state") or "<MISSING>"
        postal = j.get("zip") or "<MISSING>"
        country_code = "US"
        store_number = j.get("branchId") or "<MISSING>"
        page_url = j.get("detailBranchURL") or "<MISSING>"
        phone = j.get("phone") or "<MISSING>"
        if phone.find(",") != -1:
            phone = phone.split(",")[0].strip()
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lon") or "<MISSING>"
        location_type = "<MISSING>"

        hours = j.get("hours") or ""
        if hours:
            hours_of_operation = f"Mon-Fri: {hours}"
        else:
            continue

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
