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
    locator_domain = "https://www.backyardburgers.com"
    api_url = "https://www.backyardburgers.com/store-locator/"
    session = SgRequests()

    r = session.get(api_url)

    tree = html.fromstring(r.text)
    block = (
        "".join(tree.xpath('//script[contains(text(), "mapboxAccessToken")]/text()'))
        .split("locations:")[1]
        .split("apiKey")[0]
        .replace("}}],", "}}]")
    )
    js = json.loads(block)
    for j in js:
        location_name = j.get("name")
        street_address = j.get("street")
        city = j.get("city")
        state = j.get("state")
        slug = j.get("url")
        page_url = f"{locator_domain}{slug}"
        country_code = "US"
        postal = j.get("postal_code")
        store_number = "<MISSING>"
        latitude = j.get("lat")
        longitude = j.get("lng")
        description = "".join(j.get("description"))
        location_type = "<MISSING>"
        hours = j.get("hours")
        hours_of_operation = "<MISSING>"
        if hours:
            hours = html.fromstring(hours)
            hours_of_operation = hours.xpath("//*/text()")
            hours_of_operation = list(
                filter(None, [a.strip() for a in hours_of_operation])
            )
            hours_of_operation = (
                " ".join(hours_of_operation).replace("\xa0", "").replace("   ", " ")
            )
        if description.find("COMING SOON") != -1:
            hours_of_operation = "Coming Soon"
        if hours_of_operation.find("Hours") != -1:
            hours_of_operation = hours_of_operation.split("Hours")[1].strip()
        if hours_of_operation.find("Now Open") != -1:
            hours_of_operation = "<MISSING>"
        if hours_of_operation.find("Closed") != -1:
            hours_of_operation = "Closed"
        if hours_of_operation.find("*") != -1:
            hours_of_operation = hours_of_operation.split("*")[0].strip()
        hours_of_operation = hours_of_operation.replace("  ", " ")
        phone = j.get("phone_number") or "<MISSING>"
        if phone.find("TBD") != -1:
            phone = "<MISSING>"
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
