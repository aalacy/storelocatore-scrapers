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
    locator_domain = "https://www.wolfordshop.co.uk/"
    page_url = "https://www.wolfordshop.co.uk/stores"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[contains(text(), 'var storesJson =')]/text()"))
    text = text.split("var storesJson =")[1].strip()[:-1]
    js = json.loads(text)

    for j in js:
        street_address = j.get("address1") or "<MISSING>"
        country_code = j.get("countryCode") or "<MISSING>"

        if country_code == "US":
            city = j.get("city") or "<MISSING>"
            if "," not in city:
                line = j.get("postalCode")
                state = line.split()[0]
                postal = line.split()[-1]
            else:
                postal = j.get("postalCode")
                state = city.split(",")[-1].strip()
                city = city.split(",")[0].strip()
            if postal == state:
                state = "<MISSING>"
        elif country_code == "CA":
            postal = j.get("postalCode").replace("QC ", "")
            line = j.get("city")
            city = line.split(",")[0].strip()
            state = line.split(",")[-1].strip()
        elif country_code == "GB":
            city = j.get("city")
            state = "<MISSING>"
            postal = j.get("postalCode")
        else:
            continue

        store_number = j.get("storeID") or "<MISSING>"
        location_name = j.get("name")
        phone = j.get("phone") or "<MISSING>"
        latitude = j.get("latitude") or "<MISSING>"
        longitude = j.get("longitude") or "<MISSING>"
        location_type = "<MISSING>"
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
