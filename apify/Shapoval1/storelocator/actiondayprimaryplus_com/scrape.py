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

    locator_domain = "https://www.actiondayprimaryplus.com"
    api_url = "https://www.actiondayprimaryplus.com/locations/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath(
        '//a[./span[contains(text(), "Locations")]]/following-sibling::ul/li/a'
    )

    for d in div:

        page_url = "".join(d.xpath(".//@href"))
        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        location_name = "".join(tree.xpath('//h1[@itemprop="name"]/text()'))
        location_type = "<MISSING>"
        street_address = "".join(tree.xpath('//div[@class="street-address"]/text()'))
        phone = "".join(
            tree.xpath('//span[@class="wpseo-phone"]/a[@class="tel"]//text()')
        )
        state = "".join(tree.xpath('//span[@class="region"]/text()'))
        postal = "".join(tree.xpath('//span[@class="postal-code"]/text()'))
        country_code = "US"
        city = "".join(tree.xpath('//span[@class="locality"]/text()')).strip()
        store_number = "<MISSING>"
        latitude = (
            "".join(tree.xpath('//script[contains(text(), "phone_2nd")]/text()'))
            .split("'lat':")[1]
            .split(",")[0]
            .strip()
        )
        longitude = (
            "".join(tree.xpath('//script[contains(text(), "phone_2nd")]/text()'))
            .split("'long':")[1]
            .split(",")[0]
            .strip()
        )
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
