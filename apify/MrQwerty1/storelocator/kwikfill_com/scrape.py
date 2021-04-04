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
    locator_domain = "https://kwikfill.com/"
    api_url = "https://kwikfill.com/files/admin/modules/StoreLocator/ajax.asp?cnt=5000"

    session = SgRequests()
    r = session.get(api_url)
    tree = html.fromstring(r.text)
    li = tree.xpath("//li[@data-num]")

    for l in li:
        line = l.xpath(".//address/text()")
        line = list(filter(None, [el.strip() for el in line]))
        street_address = line[0]
        line = line[1]
        city = line.split(",")[0]
        line = line.split(",")[1].strip()
        state = line.split()[0]
        postal = line.split()[1]
        country_code = "US"
        store_number = "".join(l.xpath("./@class")).replace("item-wrap number-", "")
        page_url = "<MISSING>"
        location_name = "".join(l.xpath(".//h4/text()")).strip()
        phone = (
            "".join(l.xpath(".//a[contains(@href, 'tel')]/text()"))
            .replace("Directions", "")
            .strip()
            or "<MISSING>"
        )
        latitude = "".join(l.xpath("./@data-lat")) or "<MISSING>"
        longitude = "".join(l.xpath("./@data-lon")) or "<MISSING>"
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
