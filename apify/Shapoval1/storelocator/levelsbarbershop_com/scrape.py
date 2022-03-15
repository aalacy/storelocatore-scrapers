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
    locator_domain = "http://levelsbarbershop.com"
    page_url = "http://levelsbarbershop.com/locations.html"
    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    block = tree.xpath('//div[./div[@class="wsite-image wsite-image-border-none "]]')
    for b in block:

        ad = (
            "".join(b.xpath(".//following-sibling::*[1]//text()"))
            .replace("\n", "")
            .strip()
        )
        adr = (
            ad.split(":")[0]
            .replace("Ph", "")
            .replace("ph", "")
            .replace("Avenue NY,", "Avenue, NY,")
            .replace("Avenue Brooklyn,", "Avenue, Brooklyn,")
            .strip()
        )
        street_address = adr.split(",")[0].strip()
        phone = ad.split(":")[1].replace(" - ", "-").replace("8)5", "8) 5").strip()
        city = adr.split(",")[1].strip()
        state = adr.split(",")[2].strip()
        location_name = "".join(
            b.xpath(".//preceding-sibling::h2[1]//text()")
        ).capitalize()
        country_code = "US"
        store_number = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        location_type = "Levels barbershop"
        hours_of_operation = "<MISSING>"
        postal = "<MISSING>"

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
