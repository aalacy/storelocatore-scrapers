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
    locator_domain = "https://prestopasta.com"
    page_url = "https://prestopasta.com/locations/"
    session = SgRequests()

    r = session.get(page_url)

    tree = html.fromstring(r.text)
    block = tree.xpath("//p[./strong]")

    for b in block:

        street_address = "".join(b.xpath("./text()[1]"))
        line = "".join(b.xpath("./text()[2]"))
        city = line.split(",")[0]
        line = line.split(",")[1].strip()
        if line.find("(") != -1:
            line = line.split("(")[0].strip()
        postal = line.split()[1]
        state = line.split()[0]
        country_code = "US"
        store_number = "<MISSING>"
        location_name = "".join(b.xpath("./strong[1]/text()"))
        if location_name.find("(") != -1:
            location_name = location_name.split("(")[0].strip()
        phone = "".join(b.xpath("./text()[3]")).strip()
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = "".join(b.xpath("./text()[4]")).strip()
        if hours_of_operation.find("Open") != -1:
            hours_of_operation = hours_of_operation.split("Open")[1].strip()
        if hours_of_operation.find("Please call for hours") != -1:
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
