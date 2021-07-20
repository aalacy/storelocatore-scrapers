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
    locator_domain = "https://easternoutfitter.com/"
    page_url = "https://easternoutfitter.com/"

    session = SgRequests()

    r = session.get(page_url)
    tree = html.fromstring(r.text)
    block = tree.xpath(
        '//div[@class="site-footer-block-item  site-footer-block-rich-text  "]'
    )
    for b in block:

        ad = "".join(
            b.xpath('.//div[@class="site-footer-block-content rte"]/p[1]/text()')
        )
        adr = " ".join(ad.split()[:-1]).strip()
        street_address = adr.split(",")[0].strip()
        city = adr.split(",")[1].strip()
        postal = adr.split(",")[2].split()[1].strip()
        state = adr.split(",")[2].split()[0].strip()
        country_code = "USA"
        store_number = "<MISSING>"
        location_name = (
            "".join(b.xpath('.//h2[@class="site-footer-block-title"]//text()'))
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        phone = "".join(ad.split()[-1]).strip()
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = (
            " ".join(
                b.xpath(
                    './/div[@class="site-footer-block-content rte"]/p[position()>1]/text()'
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
