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
    locator_domain = "http://www.kimchidelight.com/"
    page_url = "http://www.kimchidelight.com/en/location.html"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//p[./strong and text()]")

    for d in divs:
        location_name = "".join(d.xpath("./strong/text()")).strip()
        line = d.xpath("./text()")
        if d.xpath("./span"):
            street_address = (
                "".join(d.xpath("./span/span/text()")) + d.xpath("./span/text()")[0]
            )
            csz = d.xpath("./span/text()")[-1].strip()
            line.insert(0, csz)
            line.insert(0, street_address)

        line = list(filter(None, [l.strip() for l in line]))

        street_address = line[0]
        city = line[1].split(",")[0].strip()
        state = line[1].split(",")[1].strip().split()[0]
        postal = line[1].split(",")[1].replace(state, "").strip()
        country_code = "CA"

        store_number = "<MISSING>"
        try:
            phone = line[2].replace("Tel:", "").strip()
        except IndexError:
            phone = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
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
