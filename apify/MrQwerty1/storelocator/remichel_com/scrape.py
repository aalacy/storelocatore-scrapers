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
    url = "https://www.remichel.com/"
    api_url = "https://www.remichel.com/WebServices/WebContent/LocateBranch/Search?city=&state=&zip=75022&distance=10000"

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()["branches"]

    for j in js:
        locator_domain = url
        street_address = j.get("streetAddress1") or "<MISSING>"
        city = j.get("city") or "<MISSING>"
        state = j.get("state") or "<MISSING>"
        postal = j.get("postalCode") or "<MISSING>"
        country_code = "US"
        store_number = j.get("branchNumber") or "<MISSING>"
        page_url = "<MISSING>"
        location_name = j.get("branchName") or "<MISSING>"
        phone = j.get("phoneNumber") or "<MISSING>"
        latitude = j.get("latitude") or "<MISSING>"
        longitude = j.get("longitude") or "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = j.get("storeDisplayHours") or "<MISSING>"

        if hours_of_operation != "<MISSING>":
            hours_of_operation = (
                hours_of_operation.replace("<br />", "; ")
                .replace("Hours (", "")
                .replace(")", ":")
                .replace("0 - 0 CST", "Closed")
                .replace("0 - 0 EST", "Closed")
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
