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

    locator_domain = "https://homebuys.com"
    page_url = "https://homebuys.com/find-a-store/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="et_pb_blurb_content"]')
    for d in div:

        location_name = "".join(d.xpath('.//h4[@class="et_pb_module_header"]//text()'))
        location_type = "Home Buys"
        street_address = "".join(
            d.xpath('.//div[@class="et_pb_blurb_description"]/p[1]/text()')
        )
        ad = "".join(
            d.xpath('.//div[@class="et_pb_blurb_description"]/p[2]/text()')
        ).strip()
        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[1].strip()
        country_code = "USA"
        city = ad.split(",")[0].strip()
        store_number = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        phone = "".join(d.xpath('.//a[contains(@href, "tel")]/text()'))
        hours_of_operation = (
            " ".join(
                d.xpath(
                    './/following::h2[text()="Store Hours:"]/following-sibling::p/text()'
                )
            )
            .replace("\n", "")
            .replace("   ", " ")
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
