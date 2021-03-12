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
    locator_domain = "https://www.dions.com"
    api_url = "https://www.dions.com/locations"

    session = SgRequests()

    r = session.get(api_url)
    tree = html.fromstring(r.text)
    block = tree.xpath('//script[contains(text(), "jQuery.extend({")]')
    for j in block:

        page_url = (
            "".join(j.xpath("./text()"))
            .split('{"content":"<a href=')[1]
            .split(">")[0]
            .replace("\/", "/")
            .replace("\/\/", "//")
        )
        session = SgRequests()
        r = session.get(page_url)
        trees = html.fromstring(r.text)

        street_address = "".join(
            trees.xpath('//span[@itemprop="streetAddress"]/text()')
        )
        city = "".join(trees.xpath('//span[@itemprop="addressLocality"]/text()'))
        postal = "".join(trees.xpath('//span[@itemprop="postalCode"]/text()'))
        state = "".join(trees.xpath('//span[@itemprop="addressRegion"]/text()'))
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        location_name = "".join(
            trees.xpath('//div[@class="heading_section"]/h1/text()')
        )
        phone = "".join(trees.xpath('//div[@class="phone_number"]/a/text()'))
        ll = "".join(
            trees.xpath(
                "//div[contains(@class, 'ee_gmap ee_gmap')]/following-sibling::script[2]/text()"
            )
        )
        latitude = ll.split('"lat":"')[1].split('"')[0]
        longitude = ll.split('"lng":"')[1].split('"')[0]
        location_type = "<MISSING>"
        hours_of_operation = (
            " ".join(trees.xpath('//div[@class="time_content"]//text()'))
            .replace("\n", "")
            .strip()
        )
        if hours_of_operation.find("*") != -1:
            hours_of_operation = hours_of_operation.split("*")[0].strip()
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
