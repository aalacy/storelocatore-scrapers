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
    locator_domain = "https://www.premierbanks.com/"
    api = "https://www.premierbanks.com/portals/premierbanks/ATMLocator/Locator/locations.xml"

    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    r = session.get(api, headers=headers)
    tree = html.fromstring(r.content)
    divs = tree.xpath("//marker")

    for d in divs:
        location_name = "".join(d.xpath("./@name"))
        slug = "".join(d.xpath("./@web"))
        page_url = f"{locator_domain}{slug}"
        adr1 = "".join(d.xpath("./@address"))
        if adr1[0].isalpha():
            adr1 = ""
        adr2 = "".join(d.xpath("./@address2")) or ""
        street_address = f"{adr1} {adr2}".strip()
        city = "".join(d.xpath("./@city"))
        state = "".join(d.xpath("./@state"))
        postal = "".join(d.xpath("./@postal"))
        country_code = "US"
        store_number = "<MISSING>"
        phone = "".join(d.xpath("./@phone"))
        latitude = "".join(d.xpath("./@lat"))
        longitude = "".join(d.xpath("./@lng"))
        location_type = "".join(d.xpath("./@type"))

        _tmp = []
        hours = ["a", "b", "c"]
        for h in hours:
            part = "".join(d.xpath(f"./@hours1{h}")).strip()
            if part:
                _tmp.append(part)

        hours_of_operation = ";".join(_tmp) or "<MISSING>"

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
