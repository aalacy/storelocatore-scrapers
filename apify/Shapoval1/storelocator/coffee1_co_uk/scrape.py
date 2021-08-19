import csv
from sgscrape.sgpostal import International_Parser, parse_address
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


def get_data():
    rows = []
    locator_domain = "https://www.coffee1.co.uk/locations/"
    api_url = "https://www.coffee1.co.uk/locations/get"
    session = SgRequests()
    r = session.get(api_url)
    js = r.json()
    for j in js:
        add = j.get("branch_address")
        address = html.fromstring(add)
        add = address.xpath("//text()")
        add = list(filter(None, [a.strip() for a in add]))
        add = " ".join(add)
        a = parse_address(International_Parser(), add)
        street_address = (
            f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
            or "<MISSING>"
        )
        city = a.city
        state = "<MISSING>"
        postal = a.postcode
        country_code = "UK"
        store_number = "<MISSING>"
        location_name = j.get("post_title")
        if location_name == "Kidderminster":
            city = location_name
        page_url = j.get("url")
        latitude = j.get("lat")
        longitude = j.get("long")
        location_type = "<MISSING>"
        hours_of_operation = "<MISSING>"
        session = SgRequests()
        r = session.get(page_url)
        tree = html.fromstring(r.text)
        phone = "".join(
            tree.xpath('////div[@class="locationmap-phone"]/text()[2]')
        ).strip()
        if phone.startswith("TBC"):
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

        rows.append(row)
    return rows


def scrape():
    data = get_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
