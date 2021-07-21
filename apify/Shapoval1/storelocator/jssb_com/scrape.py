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
    locator_domain = "https://www.jssb.com"
    api_url = "https://www.jssb.com/locations/"
    session = SgRequests()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    jsblock = (
        "".join(tree.xpath('//script[contains(text(), "locations")]/text()'))
        .split("locations:")[1]
        .split("],")[0]
        + "]"
    )
    js = json.loads(jsblock)

    for j in js:

        page_url = "https://www.jssb.com/locations/"
        location_name = "".join(j.get("customer_name"))
        street_address = f"{j.get('address1')} {j.get('address2') or ''}".replace(
            "<br>", " "
        ).strip()
        city = j.get("city")
        state = j.get("state")
        country_code = j.get("country")
        postal = j.get("zip")
        store_number = "<MISSING>"
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        location_type = j.get("branch_or_atm")
        if location_type == "atm":
            continue
        hours = j.get("hours") or "<MISSING>"
        hours_of_operation = "<MISSING>"
        if hours != "<MISSING>":
            hours = html.fromstring(hours)
            hours_of_operation = (
                " ".join(hours.xpath("//*//text()")).replace("\n", "").strip()
            )
        if hours_of_operation.find("(") != -1:
            hours_of_operation = hours_of_operation.split("(")[0].strip()
        phone = j.get("phone_number") or "<MISSING>"
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
