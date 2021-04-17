import csv

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


def get_hours(page_url):
    _tmp = []
    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    li = tree.xpath("//li[@class='f-flex f-flex-space-between']")
    for l in li:
        day = "".join(l.xpath("./span[1]/text()")).strip()
        time = "".join(l.xpath("./span[2]/text()")).strip()
        _tmp.append(f"{day} {time}")

    return ";".join(_tmp) or "<MISSING>"


def fetch_data():
    out = []
    locator_domain = "https://www.jessops.com/"
    api_url = "https://www.jessops.com/store-finder/map/pins"

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()

    for j in js:
        line = j.get("address")

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
        store_number = j.get("id") or "<MISSING>"
        page_url = f'https://www.jessops.com{j.get("url")}'
        location_name = j.get("name")
        phone = j.get("telephone") or "<MISSING>"
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = get_hours(page_url)

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
