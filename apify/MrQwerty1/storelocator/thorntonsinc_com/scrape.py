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
    url = "https://www.thorntonsinc.com/"
    api_url = "https://www.thorntonsinc.com/about-us/location-finder"

    session = SgRequests()
    r = session.get(api_url)
    tree = html.fromstring(r.text)

    js = tree.xpath("//div[@data-type='store']")

    for j in js:
        locator_domain = url
        location_name = (
            "".join(j.xpath(".//span[@data-type='name']/text()")).strip() or "<MISSING>"
        )
        street_address = (
            "".join(j.xpath(".//span[@data-type='address']/text()")).strip()
            or "<MISSING>"
        )
        city = (
            "".join(j.xpath(".//span[@data-type='city']/text()")).strip() or "<MISSING>"
        )
        state = (
            "".join(j.xpath(".//span[@data-type='state']/text()")).strip()
            or "<MISSING>"
        )
        postal = (
            "".join(j.xpath(".//span[@data-type='zip']/text()")).strip() or "<MISSING>"
        )
        country_code = "US"
        store_number = location_name.split("#")[-1].strip()
        page_url = api_url
        phone = (
            "".join(j.xpath(".//span[@data-type='phone']/text()")).strip()
            or "<MISSING>"
        )
        latitude = "".join(j.xpath("./@data-latitude")) or "<MISSING>"
        longitude = "".join(j.xpath("./@data-longitude")) or "<MISSING>"
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
