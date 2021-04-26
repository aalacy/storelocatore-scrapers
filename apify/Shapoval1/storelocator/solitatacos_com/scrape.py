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

    locator_domain = "https://solitatacos.com/"
    api_url = "https://solitatacos.com/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    block = tree.xpath('//ul[@data-menu="submenu-406"]/li/a')
    for b in block:

        page_url = "".join(b.xpath(".//@href"))
        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        location_name = "".join(
            tree.xpath('//h1[@class="hero__heading heading"]/text()')
        )
        location_type = "<MISSING>"
        adr = "".join(
            tree.xpath(
                '//p[.//a[contains(@href, "tel")]]/preceding-sibling::p[1]//text()'
            )
        )

        street_address = adr.split(",")[0].strip()
        phone = "".join(tree.xpath('//p//a[contains(@href, "tel")]/text()'))
        state = adr.split(",")[2].split()[0]
        postal = adr.split(",")[2].split()[-1]
        country_code = "USA"
        city = adr.split(",")[1].strip()
        store_number = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//p[./strong[contains(text(), "Hours of Operations")]]/text()'
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
