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

    locator_domain = "https://gimmea5.com"

    page_url = "https://gimmea5.com/locations/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    block = tree.xpath('//div[@class="wpb_column vc_column_container vc_col-sm-4"]')
    for b in block:
        location_name = (
            "".join(b.xpath(".//span/strong/text() | .//b/u/text()"))
            .replace("\n", "")
            .strip()
        )
        location_type = "<MISSING>"
        street_address = (
            "".join(
                b.xpath(
                    './/p[.//a[contains(@href, "tel")]]/text()[1] | .//p[contains(text(), "Coming Soon!")]/following-sibling::p[1]/text()[1]'
                )
            )
            .replace("\n", "")
            .strip()
        )
        ad = (
            "".join(
                b.xpath(
                    './/p[.//a[contains(@href, "tel")]]/text()[2] | .//p[contains(text(), "Coming Soon!")]/following-sibling::p[1]//text()[2]'
                )
            )
            .replace("\n", "")
            .strip()
        )

        country_code = "US"
        phone = (
            "".join(b.xpath('.//a[contains(@href, "tel")]//text()'))
            .replace("Phone:", "")
            .strip()
            or "<MISSING>"
        )
        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[-1].strip()
        city = ad.split(",")[0].strip()
        if location_name.find("Owensboro") != -1:
            postal = (
                "".join(
                    b.xpath(
                        './/p[contains(text(), "Coming Soon!")]/following-sibling::p[1]/strong/text()'
                    )
                )
                .replace("\n", "")
                .strip()
            )
        store_number = "<MISSING>"
        comsoon = "".join(b.xpath('.//p[contains(text(), "Coming Soon!")]/text()'))
        hours_of_operation = (
            " ".join(
                b.xpath(
                    '//preceding::div[@id="text-block-8"]/h4[contains(text(), "7pm")]/text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        if comsoon:
            hours_of_operation = "Coming Soon!"
        latitude = "<MISSING>"
        longitude = "<MISSING>"

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
