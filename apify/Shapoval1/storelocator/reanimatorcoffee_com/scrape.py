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
    locator_domain = "https://www.reanimatorcoffee.com"
    page_url = "https://www.reanimatorcoffee.com/pages/locations"
    session = SgRequests()

    r = session.get(page_url)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="location-info"]')
    for d in div:
        location_name = "".join(d.xpath(".//h2/text()"))
        street_address = "".join(d.xpath(".//h3/text()"))
        city = "<MISSING>"
        state = "<MISSING>"
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = (
            " ".join(d.xpath('.//div[@class="hours"]/p//text()'))
            .replace("\n", " ")
            .strip()
        )
        if hours_of_operation.find("Call") != -1:
            hours_of_operation = "<MISSING>"
        phone = "".join(d.xpath('.//a[@class="phone-number"]/text()'))
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
