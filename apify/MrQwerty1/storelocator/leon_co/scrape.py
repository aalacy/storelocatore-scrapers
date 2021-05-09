import csv
import json

from lxml import html
from sgrequests import SgRequests
from sgscrape.sgpostal import parse_address, International_Parser


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
    locator_domain = "https://leon.co/"
    api_url = "https://leon.co/all-restaurants/"

    session = SgRequests()
    r = session.get(api_url)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[@id='__NEXT_DATA__']/text()"))
    js = json.loads(text)["props"]["initialReduxState"]["data"]["restaurants"]

    for j in js:
        isclosed = j.get("closed")
        iscoming = j.get("comingSoon")

        location_name = j.get("name")
        slug = j.get("slug")
        page_url = f"https://leon.co/restaurants/{slug}"
        location_type = j.get("type") or "<MISSING>"
        line = j["locationDetails"]["fullAddress"]

        adr = parse_address(International_Parser(), line)
        street_address = (
            f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
                "None", ""
            ).strip()
            or "<MISSING>"
        )

        city = adr.city or "<MISSING>"
        state = adr.state or "<MISSING>"
        postal = adr.postcode or "<MISSING>"
        country_code = "GB"
        store_number = "<MISSING>"
        try:
            phone = j["contactDetails"]["phoneNumber"]
        except KeyError:
            phone = "<MISSING>"
        loc = j.get("geoLocation")
        latitude = loc.get("lat") or "<MISSING>"
        longitude = loc.get("lng") or "<MISSING>"

        _tmp = []
        try:
            hours = j["restaurantOpeningTimes"]["openingTimes"]
        except KeyError:
            hours = []

        for h in hours:
            day = h.get("day")
            start = h.get("opensAt")
            end = h.get("closesAt")
            _tmp.append(f"{day}: {start} - {end}")

        hours_of_operation = ";".join(_tmp) or "<MISSING>"

        if isclosed:
            hours_of_operation = "Closed"
        if iscoming:
            hours_of_operation = "Coming Soon"

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
