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
    locator_domain = "https://bankfive.com"
    api_url = "https://bankfive.com/Locations"
    session = SgRequests()
    r = session.get(api_url)
    block = r.text.split("var LocationsList = [")[1].split("]")[0]
    block = "[" + block + "]"
    js = json.loads(block)
    for j in js:
        street_address = f"{j.get('Address1')} {j.get('Address2')}".strip()
        city = j.get("City")
        postal = j.get("Zip")
        state = j.get("State")
        country_code = "US"
        store_number = "<MISSING>"
        location_name = "".join(j.get("Name"))
        phone = "".join(j.get("Phone"))
        if phone.find("(") != -1:
            phone = phone.split("(")[0].strip()
        if location_name.find("Wrentham") != -1:
            phone = j.get("Phone")
        latitude = j.get("Latitude")
        longitude = j.get("Longitude")
        location_type = j.get("Type")
        page_url = f"{locator_domain}{j.get('NodeAliasPath')}"
        session = SgRequests()
        r = session.get(page_url)
        trees = html.fromstring(r.text)
        hours_of_operation = (
            " ".join(
                trees.xpath('//h4[contains(text(), "Drive")]/preceding-sibling::text()')
            )
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        if hours_of_operation.find("by appointment") != -1:
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
