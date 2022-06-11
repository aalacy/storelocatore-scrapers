import csv
from lxml import html
from sgscrape.sgpostal import International_Parser, parse_address
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
    locator_domain = "https://www.gallowaysbakers.co.uk"
    page_url = "https://www.gallowaysbakers.co.uk/locations.php"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    div = tree.xpath(
        '//div[@class="container-fluid"]/div[@class="row"]//div[@class="shopinfo"]'
    )
    for d in div:
        line = " ".join(d.xpath("./p[1]/text()")).replace("\n", "").strip()
        a = parse_address(International_Parser(), line)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        city = a.city or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        if (
            street_address.find("18") != -1
            or street_address.find("Smithy") != -1
            or street_address.find("Unit 4") != -1
        ):
            postal = " ".join(line.split()[-2:])
        if street_address.find("Smithy") != -1:
            street_address = " ".join(line.split()[:3])
            city = "Wigan"
        if street_address.find("5B") != -1:
            street_address = "".join(line.split("Ashton-in-Makerfield")[0]).strip()
        if street_address.find("Walthew") != -1:
            city = "Wigan"
        state = a.state or "<MISSING>"
        phone = "".join(d.xpath("./p[2]/strong/text()")) or "<MISSING>"
        hours_of_operation = "<MISSING>"
        country_code = "GB"
        store_number = "<MISSING>"
        location_name = (
            "".join(d.xpath("./h2/strong/text()")).split("-")[0].strip() or "<MISSING>"
        )
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        location_type = "<MISSING>"

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
