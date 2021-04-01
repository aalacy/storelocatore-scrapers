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
    locator_domain = "https://showmars.com/"
    api_url = "https://showmars.com/locations"

    session = SgRequests()
    r = session.get(api_url)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@class='store box']")

    for d in divs:
        street_address = (
            "".join(d.xpath(".//span[@data-type='address']/text()")).strip()
            or "<MISSING>"
        )
        city = (
            "".join(d.xpath(".//span[@data-type='city']/text()")).strip() or "<MISSING>"
        )
        state = (
            "".join(d.xpath(".//span[@data-type='state']/text()")).strip()
            or "<MISSING>"
        )
        postal = (
            "".join(d.xpath(".//span[@data-type='zipcode']/text()")).strip()
            or "<MISSING>"
        )
        country_code = "US"
        store_number = "<MISSING>"
        page_url = (
            "".join(d.xpath(".//span[@data-type='morelink']/a/@href")) or "<MISSING>"
        )
        location_name = "".join(d.xpath(".//h2[@class='title']/text()")).strip()
        phone = "".join(d.xpath(".//h3/text()")).strip() or "<MISSING>"
        latitude = "".join(d.xpath("./@data-latitude")) or "<MISSING>"
        longitude = "".join(d.xpath("./@data-longitude")) or "<MISSING>"
        location_type = "<MISSING>"
        hours = d.xpath(".//span[@data-type='hours']/text()")
        hours = list(filter(None, [h.strip() for h in hours]))
        hours_of_operation = ";".join(hours) or "<MISSING>"

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
