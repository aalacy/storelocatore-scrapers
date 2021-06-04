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

    locator_domain = "https://5napkinburger.com"
    api_url = "https://5napkinburger.com/locations/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//a[contains(text(), "View More")]')
    for d in div:
        slug = "".join(d.xpath(".//@href"))
        page_url = f"{locator_domain}{slug}"
        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        location_name = "".join(tree.xpath('//h1[@class="title"]/text()'))
        location_type = "<MISSING>"
        street_address = "".join(tree.xpath('//span[@class="address_1"]/text()'))
        state = "".join(tree.xpath('//span[@class="state"]/text()'))
        postal = "".join(tree.xpath('//span[@class="zip"]/text()'))
        country_code = "USA"
        city = "".join(tree.xpath('//span[@class="city"]/text()'))
        store_number = "<MISSING>"
        latitude = "".join(tree.xpath('//span[@class="map"]/a/@data-latitude'))
        longitude = "".join(tree.xpath('//span[@class="map"]/a/@data-longitude'))
        phone = "".join(tree.xpath('//a[contains(@href, "tel")]/text()'))
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//h3[contains(text(), "Hours")]/following-sibling::div/div//text()'
                )
            )
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
