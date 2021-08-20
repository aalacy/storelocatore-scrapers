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
    locator_domain = "https://www.reeltheatre.com"
    page_url = "https://www.reeltheatre.com/locations"
    location_type = "<MISSING>"
    session = SgRequests()
    r = session.get(page_url)

    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="col-md-4 col-sm-6"]')

    for d in div:

        street_address = "".join(d.xpath('.//span[@class="address"]/text()'))
        phone = "".join(d.xpath('.//span[@class="tel"]/text()'))
        line = "".join(d.xpath('.//span[@class="city"]/text()'))
        city = line.split(",")[0]
        postal = "<MISSING>"
        state = "".join(line.split(",")[1].split())
        country_code = "US"

        store_number = "<MISSING>"
        page = "".join(d.xpath('.//h3[@class="title"]/a/@href'))
        page_url = f"{locator_domain}{page}"
        if street_address.find("131") != -1:
            page_url = "https://www.reeltheatre.com/locations"
        location_name = "".join(d.xpath('.//h3[@class="title"]/a/text()'))

        text = "".join(
            d.xpath(
                './/div[@class="col-xs-6 location-map"]/a/img[contains(@src, "center=")]/@src'
            )
        )
        latitude = text.split("center=")[1].split(",")[0]
        longitude = text.split("center=")[1].split(",")[1].split("&")[0]

        session = SgRequests()
        r = session.get(page_url)

        tree = html.fromstring(r.text)

        closed = "".join(tree.xpath('//div[@class="col-xs-12"]/h3/text()'))
        hours_of_operation = "<MISSING>"
        if closed:
            hours_of_operation = "Temporarily closed"
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
