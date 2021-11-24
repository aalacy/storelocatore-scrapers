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

    locator_domain = "https://www.tuttabella.com"
    api_url = "https://www.tuttabella.com/overview/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    jsblock = (
        "".join(tree.xpath('//script[contains(text(), "locations")]/text()'))
        .split("locations: ")[1]
        .split("apiKey")[0]
        .replace("[]}}],", "[]}}]")
        .strip()
    )
    js = json.loads(jsblock)

    for j in js:
        slug = j.get("url")
        state = j.get("state")
        page_url = f"{locator_domain}{slug}"
        location_name = j.get("name")
        location_type = "<MISSING>"
        street_address = j.get("street")
        phone = j.get("phone_number")
        postal = j.get("postal_code")
        country_code = "US"
        city = j.get("city")
        store_number = "<MISSING>"
        latitude = j.get("lat")
        longitude = j.get("lng")
        hours_of_operation = "".join(j.get("hours"))
        h = html.fromstring(hours_of_operation)
        hours_of_operation = " ".join(h.xpath("//*//text()")).replace("\n", "").strip()
        if hours_of_operation.find("Order") != -1:
            hours_of_operation = hours_of_operation.split("Order")[0].strip()

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
