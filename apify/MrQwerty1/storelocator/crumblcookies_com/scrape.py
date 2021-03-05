import csv
import json
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
    locator_domain = "https://crumblcookies.com/"
    api_url = "https://backend.crumbl.com/graphql/"
    data = {
        "query": "\n query StoresPage {\n allActiveStores {\n name\n city\n slug\n street\n zip\n state\n storeId\n email\n phone\n address\n latitude\n longitude\n storeHours {\n description\n }\n deliveryHours {\n description\n }\n }\n }\n "
    }

    session = SgRequests()
    r = session.post(api_url, data=json.dumps(data))
    js = r.json()["data"]["allActiveStores"]
    states = {"TX", "MO", "WI", "UT"}

    for j in js:
        city = j.get("city") or "<MISSING>"
        state = j.get("state") or "<MISSING>"
        postal = j.get("zip")
        street_address = j.get("street")
        for s in states:
            if s in street_address:
                street_address = street_address.split(s)[0].strip()
            if street_address[-1] == ",":
                street_address = street_address[:-1]
        country_code = "US"
        store_number = j.get("storeId").replace(":Store", "")
        page_url = f'https://crumblcookies.com/{j.get("slug")}'
        location_name = j.get("name")
        phone = j.get("phone") or "<MISSING>"
        latitude = j.get("latitude") or "<MISSING>"
        longitude = j.get("longitude") or "<MISSING>"
        location_type = "<MISSING>"
        hours = j.get("storeHours") or {}
        hours_of_operation = hours.get("description") or "<MISSING>"

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
