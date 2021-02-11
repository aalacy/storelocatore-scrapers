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
    locator_domain = "https://meamedicalclinics.com/"
    page_url = "https://meamedicalclinics.com/locations/"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    divs = tree.xpath(
        "//div[contains(@class, 'et_pb_module et_pb_toggle et_pb_toggle_')]"
    )

    for d in divs:
        line = d.xpath(".//div[@class='et_pb_toggle_content clearfix']/p[1]//text()")
        line = list(filter(None, [l.strip() for l in line]))

        location_name = line[0]

        adr = []
        phone = "<MISSING>"
        for l in line[1:]:
            if l.find("Phone") != -1 or l.count("-") == 2:
                phone = l.replace("Phone:", "").strip()
                break
            adr.append(l)

        street_address = ", ".join(adr[:-1]).replace("*", "")
        if street_address.endswith(","):
            street_address = street_address[:-1]

        adr = adr[-1]
        city = adr.split(",")[0].strip()
        adr = adr.split(",")[1].strip()
        state = adr.split()[0]
        postal = adr.split()[1]
        country_code = "US"
        store_number = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = (
            ";".join(
                d.xpath(".//div[@class='et_pb_toggle_content clearfix']/p[2]//text()")
            )
            or "<MISSING>"
        )
        if hours_of_operation.find("(") != -1:
            hours_of_operation = hours_of_operation.split("(")[0].strip()

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
