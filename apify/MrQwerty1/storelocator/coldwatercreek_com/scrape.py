import csv

from lxml import html
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
    locator_domain = "https://www.coldwatercreek.com/"
    api_url = "https://www.coldwatercreek.com/on/demandware.store/Sites-coldwater_us-Site/default/Stores-GetNearestStores?latitude=&longitude=&countryCode=US"

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()["stores"]

    for store_number, j in js.items():
        location_name = j.get("name")
        street_address = (
            f"{j.get('address1')} {j.get('address2') or ''}".strip() or "<MISSING>"
        )
        city = j.get("city") or "<MISSING>"
        state = j.get("stateCode") or "<MISSING>"
        postal = j.get("postalCode") or "<MISSING>"
        country_code = "US"
        page_url = f"https://www.coldwatercreek.com/on/demandware.store/Sites-coldwater_us-Site/default/Stores-Details?StoreID={store_number}"
        phone = j.get("phone") or "<MISSING>"
        latitude = j.get("latitude") or "<MISSING>"
        longitude = j.get("longitude") or "<MISSING>"
        location_type = "<MISSING>"

        source = j.get("storeHours") or "<html></html>"
        tree = html.fromstring(source)
        hours_of_operation = (
            ";".join(tree.xpath("//text()")).replace(".", "").strip() or "<MISSING>"
        )
        if hours_of_operation.endswith(";"):
            hours_of_operation = hours_of_operation.replace(
                "CLOSED FOR RENOVATION", "TEMPORARILY CLOSED"
            )[:-1]

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
