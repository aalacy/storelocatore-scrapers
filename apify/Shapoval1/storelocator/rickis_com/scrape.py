import csv
import json
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
    locator_domain = "https://www.rickis.com"
    api_url = "https://www.rickis.com/on/demandware.store/Sites-rickis-Site/default/Stores-GetNearestStores?latitude=51.04473309999999&longitude=-114.0718831&countryCode=CA&distanceUnit=km&maxdistance=10000"
    location_type = "<MISSING>"
    session = SgRequests()
    r = session.get(api_url)
    r = r.text.replace('{"stores": ', "").replace("}}", "}")
    js = json.loads(r)
    for j in js.values():

        street_address = f"{j.get('address1')} {j.get('address2')}".strip()
        phone = j.get("phone")
        city = j.get("city")
        postal = j.get("postalCode")
        state = j.get("stateCode")
        country_code = j.get("countryCode")
        store_number = "<MISSING>"
        page_url = "https://www.rickis.com/on/demandware.store/Sites-rickis-Site/default/Stores-Find"
        location_name = j.get("name")
        latitude = j.get("latitude")
        longitude = j.get("longitude")

        hours = "".join(j.get("storeHours")).replace("\n", " ")
        hours = html.fromstring(hours)
        hours_of_operation = (
            " ".join(hours.xpath("//*//text()")).replace("\n", "").strip()
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
