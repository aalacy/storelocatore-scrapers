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

    locator_domain = "https://www.kennedyfitness.org/"
    api_url = "https://www.kennedyfitness.org/locations/"
    session = SgRequests()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//ul[@id="menu-locations"]/li/a')

    for d in div:
        page_url = "".join(d.xpath(".//@href"))
        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        location_name = "".join(tree.xpath('//span[@class="interior-title"]/text()'))
        location_type = "<MISSING>"
        street_address = "".join(
            tree.xpath(
                '//p[contains(text(), "Address")]/following-sibling::p[1]/text()[1]'
            )
        )
        ad = (
            "".join(
                tree.xpath(
                    '//p[contains(text(), "Address")]/following-sibling::p[1]/text()[2]'
                )
            )
            .replace("\n", "")
            .strip()
        )
        phone = (
            "".join(
                tree.xpath(
                    './/div[@class="textwidget"]//a[contains(@href, "tel")]/text()'
                )
            )
            or "<MISSING>"
        )
        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[1].strip()
        city = ad.split(",")[0].strip()
        country_code = "US"
        store_number = "<MISSING>"
        map_link = "".join(tree.xpath("//iframe/@src"))
        latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
        longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//p[contains(text(), "Club Hours")]/following-sibling::p/text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        if hours_of_operation.find("Pool Hours") != -1:
            hours_of_operation = hours_of_operation.split("Pool Hours")[0].strip()

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
