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
    locator_domain = "https://www.baers.com"
    api_url = "https://www.baers.com/stores/"
    session = SgRequests()

    r = session.get(api_url)
    tree = html.fromstring(r.text)
    block = tree.xpath(
        '//div[@class="store-list l-row--mar-lg no-mar-bottom"]/div[contains(@class, "store-result")]'
    )
    for b in block:

        street_address = "".join(
            b.xpath('.//div[@class="store-result__address__street1"]/text()')
        )
        city = "".join(b.xpath('.//span[@class="store-result__address__city"]/text()'))
        postal = "".join(b.xpath('.//span[@class="store-result__address__zip"]/text()'))
        state = "".join(
            b.xpath('.//span[@class="store-result__address__state"]/text()')
        )
        country_code = "US"
        store_number = "<MISSING>"
        location_name = "".join(b.xpath('.//a[@class="store-result__name"]/text()'))

        phone = "".join(
            b.xpath(
                './/a[@class="store-result__phone store-result__phone--1 accentlink"]/text()'
            )
        )
        latitude = "".join(b.xpath(".//@data-lat"))
        longitude = "".join(b.xpath(".//@data-lon"))
        location_type = "<MISSING>"
        hours_of_operation = (
            " ".join(b.xpath('.//div[@class="store-result__hours__hours"]//text()'))
            .replace("\n", "")
            .replace("Open", "")
            .strip()
        )
        if hours_of_operation.find("Temporarily closed") != -1:
            hours_of_operation = "Closed"
        page_url = " ".join(b.xpath('.//a[@class="store-result__name"]/@href'))
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
