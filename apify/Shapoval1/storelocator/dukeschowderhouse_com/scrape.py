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

    locator_domain = "https://www.dukesseafood.com"
    api_url = "https://www.dukesseafood.com/locations/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[./a[contains(@href, "/locations/")]]/a[1]')
    for d in div:
        slug = "".join(d.xpath(".//@href"))
        location_name = (
            "".join(d.xpath('.//h3[@class="uabb-ib1-title title-center"]/text()'))
            .replace("\n", "")
            .strip()
        )
        page_url = f"{locator_domain}{slug}"
        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        location_type = "<MISSING>"
        street_address = "".join(
            tree.xpath(
                '//h3[contains(text(), "FIND US")]/following-sibling::p[1]/text()[1]'
            )
        )
        ad = (
            "".join(
                tree.xpath(
                    '//h3[contains(text(), "FIND US")]/following-sibling::p[1]/text()[2]'
                )
            )
            .replace("\n", "")
            .strip()
        )
        phone = (
            "".join(
                tree.xpath(
                    '//h3[contains(text(), "FIND US")]/following-sibling::p[2]/a[contains(@href, "tel")]/text()'
                )
            )
            .replace("Phone:", "")
            .strip()
        )
        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[-1].strip()
        country_code = "USA"
        city = ad.split(",")[0].strip()
        store_number = "<MISSING>"
        map_link = "".join(tree.xpath("//iframe/@src"))
        latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
        longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//h4[contains(text(), "HAPPY HOUR")]/preceding-sibling::*//text()'
                )
            )
            .replace("\n", "")
            .replace("HOURS", "")
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
