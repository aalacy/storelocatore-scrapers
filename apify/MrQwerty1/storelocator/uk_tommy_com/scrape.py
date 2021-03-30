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
    locator_domain = "https://uk.tommy.com/"
    page_url = "https://uk.tommy.com/store-locator"
    api_url = "https://uk.tommy.com/wcs/resources/store/30027/storelocator/byGeoNode/715837896"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0"
    }

    session = SgRequests()
    r = session.get(api_url, headers=headers)
    js = r.json()["PhysicalStore"]

    for j in js:
        street_address = ", ".join(j.get("addressLine")) or "<MISSING>"
        city = j.get("city") or "<MISSING>"
        state = "<MISSING>"
        postal = j.get("postalCode") or "<MISSING>"
        country_code = j.get("country") or "<MISSING>"
        store_number = j.get("storeName") or "<MISSING>"
        location_name = j.get("Description")[0].get("displayStoreName")
        phone = j.get("telephone1") or "<MISSING>"
        latitude = j.get("latitude") or "<MISSING>"
        longitude = j.get("longitude") or "<MISSING>"
        location_type = "<MISSING>"
        att = j.get("Attribute") or []
        hours = ""
        for a in att:
            if a.get("name") == "OpeningHours":
                hours = a.get("displayValue").replace("~~", ";")
                break

        hours_of_operation = hours or "<MISSING>"

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
