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
    locator_domain = "https://sunnin.com"
    page_url = "https://sunnin.com/locations/"

    session = SgRequests()

    r = session.get(page_url)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="wp-block-column"]')

    for d in div:
        ad = d.xpath('.//p[@class="has-text-align-center"]/text()')
        line = "".join(ad[:-1])
        street_address = line.split(",")[0]
        city = line.split(",")[1]
        line = line.split(",")[2].strip()
        postal = line.split()[1]
        state = line.split()[0]
        phone = "".join(ad[-1])
        country_code = "US"
        store_number = "<MISSING>"
        location_name = "".join(d.xpath('.//h2[@class="has-text-align-center"]/text()'))
        hours_of_operation = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        location_type = "<MISSING>"
        if street_address.find("1776") != -1:
            session = SgRequests()
            rr = session.get("http://sunnin.com/contact-us/")
            trees = html.fromstring(rr.text)
            hours_of_operation = "".join(
                trees.xpath("//p[contains(text(), 'am')]//text()")
            )
            ll = "".join(trees.xpath("//iframe/@src"))
            latitude = ll.split("!3d")[1].strip().split("!")[0].strip()
            longitude = ll.split("!2d")[1].strip().split("!")[0].strip()

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
