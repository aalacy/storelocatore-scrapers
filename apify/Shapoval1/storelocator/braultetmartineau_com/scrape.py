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

    locator_domain = "https://www.braultetmartineau.com"
    page_url = "https://www.braultetmartineau.com/en/store-finder?InitMap=true"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="store-list-address col-md-3 col-xs-12 col-sm-6"]')

    for d in div:

        location_name = "".join(d.xpath(".//address/text()[1]"))
        location_type = "Store"
        street_address = "".join(d.xpath('.//span[@class="addressline1"]/text()'))
        phone = "".join(d.xpath('.//span[@class="phonebusiness"]/text()'))
        state = "".join(d.xpath('.//span[@class="province"]/text()'))
        postal = "".join(d.xpath('.//span[@class="postalcode"]/text()'))
        country_code = "".join(d.xpath('.//span[@class="countryname"]/text()'))
        city = "".join(d.xpath('.//span[@class="city"]/text()'))
        store_number = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hours_of_operation = (
            " ".join(d.xpath('.//span[contains(@class, "store-opening-hours")]/text()'))
            .replace("\n", "")
            .strip()
        )

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
